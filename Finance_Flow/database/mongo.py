import pymongo

connection_url = "mongodb+srv://iamvishalpoddar:Vip01245@cluster0.fwfq66x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

my_client = pymongo.MongoClient(connection_url)

reg_db = my_client['Registration']
finance_db = my_client['Finance']
budget_db = my_client['Budget']