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
        model: "gpt-4.0-turbo",
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