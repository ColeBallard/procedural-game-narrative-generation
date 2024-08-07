import os

import json
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from .prompt_templates import WORLD_BUILDING_LOCATIONS

from .orm import Location

class WorldBuilding:
    def __init__(self, seed_data, seed_id, session, openai, model):
        self.seed_data = seed_data
        self.seed_id = seed_id
        self.session = session
        self.openai = openai
        self.model = model

    def generate_locations(self):
        prompt = WORLD_BUILDING_LOCATIONS.format(self.seed_data)

        response = self.openai.chat.completions.create(
            model=self.model,  # Use the appropriate model engine
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )

        return response.choices[0].message.content.strip()
    
    def extract_json(self, text):
        """
        Extracts the JSON part from the text.
        """
        try:
            start_index = text.index("[")
            end_index = text.rindex("]") + 1
            json_str = text[start_index:end_index]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            print("Failed to extract or parse JSON:", e)
            return None

    def create_locations(self):
        location_text = self.generate_locations()

        print(location_text)

        # Parse the generated location data
        locations = self.extract_json(location_text)
        if locations is None:
            return {"message": "Failed to generate location data", "status": "failure"}

        try:
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
            return {"message": "Locations created successfully", "status": "success"}
        except IntegrityError:
            self.session.rollback()
            return {"message": "Database error during location creation", "status": "failure"}
