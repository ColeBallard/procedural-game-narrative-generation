import sys
import json
import traceback
from datetime import datetime, timedelta
import random

from .prompt_templates import WORLD_BUILDING

from .orm import Seed, Character, Skill, CharacterSkill, Status, CharacterStatus, Location, Event, EventCharacter

class WorldBuilding:
    def __init__(self, seed_data, seed_id, session, openai, model):
        self.seed_data = seed_data
        self.seed_id = seed_id
        self.session = session
        self.openai = openai
        self.model = model
          
    def create_main_character(self):
        retries = 0
        max_retries = 5
        while True:
            character_text = self.get_gpt_response(WORLD_BUILDING['MAIN_CHARACTER'].format(self.seed_data))

            character_data = self.extract_json(character_text)

            if character_data is None:
                print("No valid JSON data was extracted.")
                return {"message": "Failed to create main character due to invalid data", "status": "failure"}

            # Adding random attributes if they are not set
            stats = ['strength', 'speed', 'agility', 'intelligence', 'wisdom', 'charisma']
            for stat in stats:
                if stat not in character_data or character_data[stat] is None:
                    character_data[stat] = random.randint(8, 16)  # Ensure all stats have a value

            try:
                new_character = Character(
                    seed_id=self.seed_id,
                    main_character=1,  # True as this is the main character
                    alive=1,  # Initially alive
                    name=character_data['name'],
                    date_of_birth=character_data['date_of_birth'],
                    race=character_data['race'],
                    gender=character_data['gender'],
                    level=1,  # Starts at level 1
                    exp_points=0,  # No experience points initially
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    strength=character_data['strength'],
                    speed=character_data['speed'],
                    agility=character_data['agility'],
                    intelligence=character_data['intelligence'],
                    wisdom=character_data['wisdom'],
                    charisma=character_data['charisma'],
                    current_health=100,
                    max_health=100,
                    current_currency=0  # No currency initially
                )
                self.session.add(new_character)
                self.session.commit()

                if 'current_date_time' in character_data:
                    # Fetch the seed record by seed_id
                    seed = self.session.query(Seed).filter(Seed.id == self.seed_id).one()
                    
                    # Update the current_date_time
                    seed.current_date_time = character_data['current_date_time']

                    # Commit the changes to the database
                    self.session.commit()

                self.character_data = character_data
                self.character_data['id'] = new_character.id

                return {"message": "Main character created successfully", "status": "success"}
            except Exception as e:
                retries += 1
                self.session.rollback()
                if retries > max_retries:
                    print(f'Exceeded max try limit for main character. Unable to properly world build.')
                    return {"message": f"Failed to create main character. {e}", "status": "failure"}
                else:
                    print(f'Error occured for main character world building. Retrying attempt {retries}/{max_retries}. {e}.')

    def create_main_character_skills(self):
        retries = 0
        max_retries = 5

        while retries <= max_retries:
            skills_text = self.get_gpt_response(WORLD_BUILDING['MAIN_CHARACTER_SKILLS'].format(self.character_data, self.seed_data))
            skills_data = self.extract_json(skills_text, list_flag=True)

            if skills_data is None:
                print("No valid JSON data was extracted for skills.")
                retries += 1
                continue

            try:
                for skill in skills_data:
                    # Create a new Skill instance
                    new_skill = Skill(
                        name=skill['name'],
                        description=skill['description'],
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    self.session.add(new_skill)
                    self.session.flush()  # Flush to get the skill_id before committing

                    # Create a CharacterSkill instance linking the character to the new skill
                    new_character_skill = CharacterSkill(
                        seed_id=self.seed_id,
                        character_id=self.character_data['id'],  # Assume character_data has the character's id
                        skill_id=new_skill.id,
                        level=1,  # Randomly assign a level or based on some logic
                        exp_points=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    self.session.add(new_character_skill)

                self.character_data['skills'] = skills_data

                self.session.commit()
                return {"message": "Main character skills created successfully", "status": "success"}

            except Exception as e:
                self.session.rollback()
                retries += 1
                if retries > max_retries:
                    print(f'Exceeded max try limit for main character skills. Unable to properly world build.')
                    return {"message": f"Failed to create main character skills. {e}", "status": "failure"}
                else:
                    print(f'Error occurred for main character skills world building. Retrying attempt {retries}/{max_retries}. {e}')

        return {"message": "Failed to create main character skills after multiple attempts.", "status": "failure"}
    
    def create_main_character_statuses(self):
        retries = 0
        max_retries = 5

        while retries <= max_retries:
            statuses_text = self.get_gpt_response(WORLD_BUILDING['MAIN_CHARACTER_STATUSES'].format(self.character_data, self.seed_data))
            statuses_data = self.extract_json(statuses_text, list_flag=True)

            if statuses_data is None:
                print("No valid JSON data was extracted for statuses.")
                retries += 1
                continue

            try:
                for status in statuses_data:
                    # Create a new Status instance
                    new_status = Status(
                        name=status['name'],
                        description=status['description'],
                        type=status['type'],
                        duration=status.get('duration', 0),  # Default duration to 0 if not specified
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    self.session.add(new_status)
                    self.session.flush()  # Flush to get the status_id before committing

                    # Create a CharacterStatus instance linking the character to the new status
                    new_character_status = CharacterStatus(
                        seed_id=self.seed_id,
                        character_id=self.character_data['id'],  # Assume character_data has the character's id
                        status_id=new_status.id,
                        active=False,  # Assume the status is initially active
                        end_date_time=datetime.now(),  # Calculate end time if applicable
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    self.session.add(new_character_status)

                self.character_data['statuses'] = statuses_data  # Store for any further processing

                self.session.commit()
                return {"message": "Main character statuses created successfully", "status": "success"}

            except Exception as e:
                self.session.rollback()
                retries += 1
                if retries > max_retries:
                    print(f'Exceeded max try limit for main character statuses. Unable to properly world build.')
                    return {"message": f"Failed to create main character statuses. {e}", "status": "failure"}
                else:
                    print(f'Error occurred for main character statuses world building. Retrying attempt {retries}/{max_retries}. {e}')

        return {"message": "Failed to create main character statuses after multiple attempts.", "status": "failure"}

    def create_locations(self):
        retries = 0
        max_retries = 5
        while True:
            try:
                location_text = self.get_gpt_response(WORLD_BUILDING['LOCATIONS'].format(self.seed_data))

                # Parse the generated location data
                locations = self.extract_json(location_text, list_flag=True)
                if locations is None:
                    return {"message": "Failed to generate location data", "status": "failure"}

                for loc in locations:
                    new_location = Location(
                        seed_id=self.seed_id,
                        name=loc['name'],
                        description=loc['description'],
                        longitude=loc.get('longitude'),
                        latitude=loc.get('latitude'),
                        type=loc.get('type'),
                        climate=loc.get('climate'),
                        terrain=loc.get('terrain'),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    self.session.add(new_location)
                    self.session.commit()

                    loc['id'] = new_location.id

                    sub_retries = 0
                    max_sub_retries = 5

                    while True:
                        try:
                            sub_location_text = self.get_gpt_response(WORLD_BUILDING['SUB_LOCATIONS'].format(loc, self.seed_data))

                            sub_locations = self.extract_json(sub_location_text, list_flag=True)

                            for sub_loc in sub_locations:
                                new_sub_location = Location(
                                    seed_id=self.seed_id,
                                    name=sub_loc['name'],
                                    description=sub_loc['description'],
                                    longitude=sub_loc.get('longitude'),
                                    latitude=sub_loc.get('latitude'),
                                    type=sub_loc.get('type'),
                                    climate=sub_loc.get('climate'),
                                    terrain=sub_loc.get('terrain'),
                                    parent_id=new_location.id,
                                    created_at=datetime.now(),
                                    updated_at=datetime.now()
                                )
                                self.session.add(new_sub_location)

                            self.session.commit()
                            break
                            
                        except Exception as e:
                            sub_retries += 1
                            self.session.rollback()
                            if sub_retries > max_sub_retries:
                                print(f'Exceeded max try limit for sub locations. Location {loc['name']} will have no sub-locations.')
                                break
                            else:
                                print(f'Error occured for sub location world building. Retrying attempt {sub_retries}/{max_sub_retries}. {e}.')

                self.locations = locations
                return {"message": "Locations created successfully", "status": "success"}
            except Exception as e:
                retries += 1
                self.session.rollback()
                if retries > max_retries:
                    print(f'Exceeded max try limit for locations. Unable to properly world build.')
                    return {"message": f"Error during location creation. {e}", "status": "failure"}
                else:
                    # Correctly capture the exception info using sys.exc_info()
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    # Format traceback and extract the last entry
                    tb_info = traceback.format_tb(exc_traceback)[-1]
                    tb_file, tb_line, tb_func, tb_text = tb_info.strip().split('\n')[0].split(',')
                    tb_file = tb_file.strip().split('"')[1]  # Clean up filename output
                    tb_line = tb_line.strip().split()[1]  # Extract line number
                    
                    print(f'Error occurred for location world building on {tb_file} line {tb_line} in {tb_func}.')
                    print(f'Retrying attempt {retries}/{max_retries}. Error: {exc_type.__name__}: {e}.')

    def create_surrounding_characters(self):
        retries = 0
        max_retries = 5
        while retries <= max_retries:
            try:
                for location in self.locations:
                    characters_text = self.get_gpt_response(WORLD_BUILDING['SURROUNDING_CHARACTERS'].format(location, self.seed_data))
                    characters_data = self.extract_json(characters_text, list_flag=True)

                    if characters_data is None:
                        print("No valid JSON data was extracted for surrounding characters.")
                        retries += 1
                        continue

                    for character in characters_data:
                        level = random.randint(1, 3)
                                             
                        new_character = Character(
                            seed_id=self.seed_id,
                            main_character=False,
                            alive=True,
                            name=character['name'],
                            date_of_birth=character['date_of_birth'],
                            race=character['race'],
                            gender=character['gender'],
                            level=level,
                            exp_points=100*((2**(level-1))-1),
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            strength=random.randint(4, 16)+level,
                            speed=random.randint(4, 16)+level,
                            agility=random.randint(4, 16)+level,
                            intelligence=random.randint(4, 16)+level,
                            wisdom=random.randint(4, 16)+level,
                            charisma=random.randint(4, 16)+level,
                            current_health=100*level,
                            max_health=100*level,
                            current_currency=random.randint(0, 1000)
                        )
                        self.session.add(new_character)
                        self.session.flush()  # Flush to ensure new_character.id is available

                        # Generate and assign events to the new character
                        event_data = self.get_gpt_response(WORLD_BUILDING['CHARACTER_EVENT'].format(character, location, self.seed_data))
                        new_event = Event(
                            seed_id=self.seed_id,
                            name=event_data['name'],
                            description=event_data['description'],
                            start_date_time=self.character_data['current_date_time'] - timedelta(hours=random.randint(1, 5)) if self.character_data['current_date_time'] else None,
                            end_date_time=self.character_data['current_date_time'] if self.character_data['current_date_time'] else None,
                            type=event_data['type'],
                            location_id=location['id'],
                            start_turn=1,
                            end_turn=1,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        self.session.add(new_event)
                        self.session.flush()  # Flush to ensure new_event.id is available

                        new_event_character = EventCharacter(
                            seed_id=self.seed_id,
                            character_id=new_character.id,
                            event_id=new_event.id,
                            role=event_data['role'],
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        self.session.add(new_event_character)
                    
                        self.session.commit()  # Commit after processing each location
                return {"message": "Surrounding characters and their events created successfully", "status": "success"}
            except Exception as e:
                self.session.rollback()
                retries += 1
                if retries > max_retries:
                    print(f'Exceeded max try limit for creating surrounding characters. {e}')
                    return {"message": "Failed to create surrounding characters. Retry limit exceeded.", "status": "failure"}
                else:
                    print(f'Error occurred while creating surrounding characters. Retrying... {e}')
        return {"message": "Failed to create surrounding characters after multiple attempts.", "status": "failure"}

    def get_gpt_response(self, prompt):
        response = self.openai.chat.completions.create(
            model=self.model,  # Use the appropriate model engine
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )

        return response.choices[0].message.content.strip()

    def extract_json(self, text, list_flag=False):
        """
        Extracts the JSON part from the text.
        """
        try:
            if list_flag:
                start_index = text.index("[")
                end_index = text.rindex("]") + 1
            else:
                start_index = text.index("{")
                end_index = text.rindex("}") + 1

            json_str = text[start_index:end_index]

            json_obj = json.loads(json_str)

            if not list_flag:
                # Define mapping of JSON fields to expected internal fields
                field_map = {
                    'name': ['character_name', 'name'],
                    'date_of_birth': ['date_of_birth', 'birth_date'],
                    'race': ['race', 'character_race'],
                    'gender': ['gender', 'character_gender'],
                    'current_date_time': ['current_date_time', 'current_datetime']
                }

                # Remap fields
                json_obj = self.remap_fields(json_obj, field_map)

                if 'gender' in json_obj:
                    # Convert gender to boolean before insertion
                    gender_map = {'Female': False, 'Male': True}
                    json_obj['gender'] = gender_map.get(json_obj['gender'], None)  # default None if gender is not recognized

                if 'date_of_birth' in json_obj:
                    # Example of handling date parsing and other data manipulations
                    try:
                        json_obj['date_of_birth'] = datetime.strptime(json_obj['date_of_birth'], "%Y-%m-%d")
                    except Exception as e:
                        print(f"Can't format date {json_obj['date_of_birth']}.")
                        json_obj['date_of_birth'] = None  # Handle invalid date formats gracefully

            return json_obj
        except (ValueError, json.JSONDecodeError) as e:
            print("Failed to extract or parse JSON:", e)
            return None
        
    def remap_fields(self, character_data, field_map):
        """
        Remaps fields in character_data based on field_map.
        """
        remapped_data = {}
        for standard_field, possible_fields in field_map.items():
            for field in possible_fields:
                if field in character_data:
                    remapped_data[standard_field] = character_data[field]
                    break
            else:
                print(f"Warning: Missing expected field '{standard_field}' in character data.")
                remapped_data[standard_field] = None  # or set a default value if necessary
        return remapped_data