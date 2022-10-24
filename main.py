
from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import pandas as pd
import sqlite3

app = Flask(__name__)
###############################################################################################################
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda:'Gold Challenge - Indonesian Abusive and Hate Speech Tweet Text'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'Cleansing Tweet Abusive and Hate Speech')
        }, host = LazyString(lambda: request.host)
    )
swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
    }
swagger = Swagger(app, template=swagger_template, config=swagger_config)

###############################################################################################################
# Connection ke db SQLite

db = sqlite3.connect('Gold_Binar.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()      
        
###############################################################################################################

#Data Tweet
df = pd.read_sql_query('SELECT * FROM data_tweet', db)
df = pd.DataFrame(df, columns = ['Tweet'])
df['id'] = range(0,len(df))
df['id'] = df['id'].astype('int')
df.index = df['id']

list_tweet = df['Tweet'].tolist()

#data Abusive
df1 = pd.read_sql_query('SELECT * FROM abusive', db)
df1 = pd.DataFrame(df1, columns =['abusive'] )
df1['id'] = range(0, len(df1))
df1['id'] = df1['id'].astype('int')
df1.index = df1['id']

list_abusive = df1['abusive'].tolist()

#data alay
df2 = pd.read_sql_query('SELECT * FROM new_kamusalay', db)
df2 = pd.DataFrame(df2, columns =['alay'] )
df2['id'] = range(0, len(df2))
df2['id'] = df2['id'].astype('int')
df2.index = df2['id']

list_alay = df2['alay'].tolist()

#data fix alay
df3 = pd.read_sql_query('SELECT * FROM new_kamusalay', db)
df3 = pd.DataFrame(df3, columns =['fix_alay'] )
df3['id'] = range(0, len(df3))
df3['id'] = df3['id'].astype('int')
df3.index = df3['id']

list_alay_fix = df3['fix_alay'].tolist()


###############################################################################################################
def frame(df, list_abusive):
    df_get = df.copy()
    df_get['new_tweet'] = df['Tweet'].str.lower().tolist()

    list_tweet = df_get['new_tweet'].tolist()
    
    for i in list_tweet:
        for j in list_abusive:
            if j in i:
              k = list_tweet[list_tweet.index(i)].replace(j,'*****')
              list_tweet[list_tweet.index(i)] = k
              i = k
    
    df_get['new_tweet'] = list_tweet
    json = df_get.to_dict(orient='index')

    del df_get

    return json

###############################################################################################################
# GET 'It works!'
@swag_from("docs/index.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def test():
	return jsonify({'message' : 'It works!'})

###############################################################################################################
# GET All Tweet

#GET
@swag_from("docs/index.yml", methods=['GET'])
@app.route('/tweet', methods=['GET'])
def returnAll():
    #json = frame(df)
    json = frame(df, list_tweet)
     
    return jsonify(json)


###############################################################################################################
# GET Spesifik Tweet
@swag_from("docs/tweet.yml", methods=['GET'])
@app.route('/tweet/<id>', methods=['GET'])
def returnOne(id):
    
    json = frame(df, list_abusive)
    
    id = int(id)
    json = json[id]

    return jsonify(json)



###############################################################################################################
# Insert New Tweet - POST Json     
              
@swag_from("docs/tweet_post.yml", methods=['POST'])
@app.route('/tweet', methods=['POST'])
def addOne():

    new_tweet = {'Tweet': request.json['Tweet']}
    df.loc[len(df)+1]=[new_tweet['Tweet'],max(df['id'])+1]
    df.index = df['id']
    json = frame(df, list_abusive)
    
    id = max(df.index)
    json = json[id]
    
    return jsonify(json)
    df.to_sql('Tweet', con=db, if_exists='append', index=False)


###############################################################################################################
# POST Upload


@swag_from("docs/tweet_upload.yml", methods=['POST'])
@app.route("/tweet/file", methods=["POST"])

def post_file():
    file = request.files[file]
    df = pd.read_csv(file)
    json = frame(df, list_abusive)
    id = max(df.index)
    json = json[id]
    return jsonify(json)

###############################################################################################################

# Update - PUT

@swag_from("docs/tweet_put.yml", methods=['PUT'])
@app.route('/tweet/<id>', methods=['PUT'])
def editOne(id):
    tweet = {'tweet': request.json['tweet']}
    id = int(id)

    if id in df['id'].tolist():
        df.loc[id] = [tweet['tweet'],id]

        json = frame(df, list_abusive)

        json = json[id]

        return jsonify(json)
    else :
        return 'input ulang'

###############################################################################################################
#DELETE
@swag_from("docs/tweet_delete.yml", methods=['DELETE'])
@app.route('/tweet/<id>', methods=['DELETE'])
def removeOne(id):
    # hapus = [df for df in df if df['id']]
    # df.remove(hapus[0])
    
    global df
    id = int(id)
    df = df.drop(id)
    
    
    json = frame(df, list_tweet)
    
    return jsonify(json)



###############################################################################################################
# Run Flask
if __name__ == "__main__":
    app.run()