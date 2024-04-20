$(document).ready(function () {
    loadUserData();

    $('#game-view').hide();
    $('#options-view').show();

    changeTabViews('api-keys', ['new-game', 'game-view', 'story-settings']);

    $('#options-view-btn').click(function (e) {
        e.preventDefault();
        $('#game-view').hide();
        $('#options-view').show();
    });

    $('#game-view-btn').click(function (e) {
        e.preventDefault();
        $('#game-view').show();
        $('#options-view').hide();
    });

    setTabClickEvents(['new-game', 'load-game', 'story-settings', 'api-keys']);

    $('#save-api-keys-btn').click(function (e) {
        e.preventDefault();
        saveUserData();
    });

    $('#book-writer-form').on('submit', function (e) {
        e.preventDefault();

        // Clear previous error messages
        $('.error').text('');

        // Validation
        let isValid = true;

        if ($('#book-writer-title').val().trim() === '') {
            $('#book-writer-title-Error').text('Please enter a title.');
            isValid = false;
        }

        if (!isValid) {
            return; // Stop the function if validation fails
        }

        prefix = 'book-writer'

        // Show the loading bar
        $('#' + prefix + '-loading-bar-container').show();
        $('#' + prefix + '-loading-bar').css('width', '0%');
        $('#' + prefix + '-loading-percent').text('0%'); // Reset the text

        let formData = gatherFormData();
        formData['title'] = $('#book-writer-title').val().trim();
        formData["api_key"] = $("#openai-api-key-input").val();

        $.ajax({
            type: "POST",
            url: "/book-writer",
            contentType: "application/json",
            data: JSON.stringify(formData),
            xhr: function () {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function (evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total;
                        // Update loading bar width
                        $('#' + prefix + '-loading-bar').css('width', percentComplete * 100 + '%');
                    }
                }, false);
                return xhr;
            },
            success: function (response) {
                console.log("Data submitted successfully:", response);
            },
            error: function (xhr, status, error) {
                console.error("Error in data submission:", xhr.responseText);
            },
            complete: function () {
                // Hide the loading bar when the request is complete
                updateLoadingBar(formData.title, prefix);
            }
        });
    });

});

function changeTabViews(active_tab, inactive_tabs) {
    $(`#${active_tab}-view`).show();
    $(`#${active_tab}-tab`).addClass('active');

    for (let inactive_tab of inactive_tabs) {
        $(`#${inactive_tab}-view`).hide();
        $(`#${inactive_tab}-tab`).removeClass('active');
    }
}

function setTabClickEvents(tabs) {
    for (let tab of tabs) {
        $(`#${tab}-tab`).click(function (e) {
            e.preventDefault();
            const other_tabs = tabs.filter(t => t !== tab);
            changeTabViews(tab, other_tabs);
        });
    }
}

function gatherFormData() {
    let selectedPromptType = $('#book-writer-prompt-type').val();
    let formData = {};

    if (selectedPromptType === 'Outline') {
        let inputData = [];
        $('#inputContainer').find('.input-group').each(function () {
            let level = $(this).find('.level-indicator').text();
            let value = $(this).find('input[type="text"]').val();
            inputData.push({ value: value, level: level });
        });
        formData['outline'] = inputData;
    } else if (selectedPromptType === 'Summary') {
        formData['summary'] = $('#summaryTextarea').val().trim();
    }

    return formData;
}

function setOpenAIApiKeyLocalStorageItem(value) {
    localStorage.setItem('key15-62689134', value);
}

function getOpenAIApiKeyLocalStorageItem() {
    return localStorage.getItem('key15-62689134');
}

function setGroqApiKeyLocalStorageItem(value) {
    localStorage.setItem('key73-41976154', value);
}

function getGroqApiKeyLocalStorageItem() {
    return localStorage.getItem('key73-41976154');
}

function saveUserData() {
    var openai_api_key = $("#openai-api-key-input").val();
    setOpenAIApiKeyLocalStorageItem(openai_api_key);

    var groq_api_key = $("#groq-api-key-input").val();
    setGroqApiKeyLocalStorageItem(groq_api_key);
}

function loadUserData() {
    var openai_api_key = getOpenAIApiKeyLocalStorageItem();

    if (openai_api_key)
        $("#openai-api-key-input").val(openai_api_key);

    var groq_api_key = getGroqApiKeyLocalStorageItem();

    if (groq_api_key)
        $("#groq-api-key-input").val(groq_api_key);
}

async function testOpenAIKey() {
    var apiKey = $("#openai-api-key-input").val();

    const url = 'https://api.openai.com/v1/chat/completions'; // Example endpoint

    const headers = {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
    };

    const body = JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
            {
                role: "system",
                content: "You are a helpful assistant."
            },
            {
                role: "user",
                content: "Hello!"
            }
        ]
    });

    try {
        const response = await fetch(url, { method: 'POST', headers: headers, body: body });
        const data = await response.json();

        if (response.ok) {
            return { valid: true, message: 'API key is valid.', data: data };
        } else {
            return { valid: false, message: 'API key is not valid.', error: data };
        }
    } catch (error) {
        return { valid: false, message: 'Failed to test API key.', error: error };
    }
}

// Function to periodically fetch progress and update the loading bar
function updateLoadingBar(title, prefix) {
    $.get('/progress', function (data) {
        if (data.current && data.total) {
            var progress = (data.current / data.total) * 100;
            $('#' + prefix + '-loading-bar').css('width', progress + '%');
            $('#' + prefix + '-loading-percent').text(Math.round(progress) + '%'); // Update the text
        }

        if (data.complete) {
            deliverPDF(data.text, title);
            // Hide the loading bar when processing is complete
            $('#' + prefix + '-loading-bar-container').hide();
        }
        else {
            setTimeout(() => updateLoadingBar(title, prefix), 1000); // Update every second
        }
    });
}