import pymongo
import dns

class Connection():
    def __init__(self, *args, **kwargs):
        self.client = pymongo.MongoClient("mongodb+srv://PuddingTeacher:D2TBaphcSrMCldaC@puddingdong.7odsp.mongodb.net/PudDingDong?retryWrites=true&w=majority")
        self.db = self.client.PuddingTeacher
        self.recipe = self.db.Recipe
        self.recipeURL = self.db.RecipeURL

    def insertRecipe(self, Info):
        self.recipe.insert_one(
            {
                "URL": Info['URL'],
                "title": Info['title'],
                "image": Info['image'],
                "author": Info['author'],
                "description": Info['description'],
                'serving': Info['serving'],
                'time_needed': Info['time_needed'],
                'ingredients': Info['ingredients'],
                'steps': Info['steps'],
                'tip': Info['tip'],
                'release_time': Info['release_time']
            }
        )

    def recordRecipeURL(self, URL):
        self.recipeURL.insert_one({"URL": URL})

    def getAllRecipeURL(self):
        recipe_URL_list = []
        links = list(self.recipeURL.find({}, {'_id':0}))
        for link in links:
            recipe_URL_list.append(link['URL'])
        return recipe_URL_list
