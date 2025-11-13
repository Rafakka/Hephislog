from modules.recipe_normalizer.normalize import recipe_normalizer

recipe_test = {
  "title": "Massa de panqueca simples",
  "ingredients": [
    "1 ovo",
    "1 xícara de farinha de trigo",
    "1 xícara de leite",
    "1 pitada de sal",
    "1 colher (sopa) de óleo"
  ],
  "steps": [
    "1 Bata todos os ingredientes no liquidificador até obter uma consistência cremosa.",
    "2 Unte uma frigideira com óleo e despeje uma concha de massa.",
    "3 Faça movimentos circulares para que a massa se espalhe por toda a frigideira.",
    "4 Espere até a massa se soltar do fundo, vire e deixe fritar do outro lado.",
    "5 Acrescente o recheio de sua preferência , enrole e está pronta para servir."
  ],
  "info": {}
}

formatted_recipe = recipe_normalizer(recipe_test)
print(formatted_recipe)