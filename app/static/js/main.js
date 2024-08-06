// js/main.js
import { changeTabViews, setTabClickEvents } from './ui/tabs.js';
import { setLocalStorageItem, getLocalStorageItem } from './utils/storage.js';

$(document).ready(function () {
    // Loading API keys from local storage
    const openaiApiKey = getLocalStorageItem('key15-62689134');
    const groqApiKey = getLocalStorageItem('key73-41976154');

    if (openaiApiKey) {
        $("#openai-api-key-input").val(openaiApiKey);
    }
    if (groqApiKey) {
        $("#groq-api-key-input").val(groqApiKey);
    }

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
        setLocalStorageItem('key15-62689134', $("#openai-api-key-input").val());
        setLocalStorageItem('key73-41976154', $("#groq-api-key-input").val());
    });

});
