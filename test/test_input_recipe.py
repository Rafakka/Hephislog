from modules.recipe_normalizer.normalize import recipe_normalizer

def test_recipe_normalizer_basic():
    sample = {
        "title": "Massa de panqueca simples",
        "ingredients": ["1 ovo", "1 xícara de farinha"],
        "steps": ["1 Bata tudo", "2 Misture bem"],
        "info": {}
    }

    result = recipe_normalizer(sample)

    assert result["success"] is True
    assert "data" in result
    assert result["data"]["name"] == "Massa De Panqueca Simples"
    assert len(result["data"]["ingredients"]) == 2
