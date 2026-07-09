import json
from mask_tool import i18n
from mask_tool.i18n import STRINGS, LANGS, tr, set_lang, load_lang, save_lang


def test_every_key_has_all_languages():
    for key, entry in STRINGS.items():
        assert set(entry.keys()) == set(LANGS), key
        for lang in LANGS:
            assert isinstance(entry[lang], str) and entry[lang], (key, lang)


def test_default_language_is_english(tmp_path):
    lang = load_lang(str(tmp_path / "missing.json"))
    assert lang == "en"
    assert tr("err_title") == "Error"


def test_set_lang_switches_strings():
    set_lang("zh")
    assert tr("err_title") == "错误"
    set_lang("en")
    assert tr("err_title") == "Error"


def test_save_then_load_roundtrip(tmp_path):
    path = str(tmp_path / "settings.json")
    save_lang("zh", path)
    assert load_lang(path) == "zh"
    with open(path, "r", encoding="utf-8") as f:
        assert json.load(f) == {"lang": "zh"}
    save_lang("en", path)   # restore module default for other tests
    assert load_lang(path) == "en"


def test_invalid_lang_falls_back_to_english(tmp_path):
    path = str(tmp_path / "settings.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"lang": "fr"}, f)
    assert load_lang(path) == "en"
    set_lang("fr")   # ignored
    assert i18n.current_lang() == "en"
