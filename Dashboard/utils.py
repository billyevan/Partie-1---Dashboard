import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

'''This file contains the functions used to extract the data from the graph (and dataframes) and to prepare it for the dashboard'''

# Load the graph
# G = nx.read_graphml('database_formated_for_NetworkX.graphml')

# Function to measure the number of interactions for each type of event
def mesure_activity_intensity(G, event_type):
    event_ids = [data.get('id') for node, data in G.nodes(data=True)
                 if data.get('labels') == ':Event' and data.get('eventType') == event_type]
    event_metrics = []
    for event_id in event_ids:
        tweets = [source for source, target, data in G.edges(data=True)
                  if data.get('label') == 'IS_ABOUT' and G.nodes[target].get('id') == event_id]
        event_subgraph = G.subgraph(tweets)
        num_tweets = event_subgraph.number_of_nodes()
        num_retweets = sum(1 for _, _, data in event_subgraph.edges(data=True) if data.get('label') == 'RETWEETED')
        num_replies = sum(1 for _, _, data in event_subgraph.edges(data=True) if data.get('label') == 'REPLY_TO')
        event_metrics.append({
            'Event ID': event_id,
            'Tweets': num_tweets,
            'Retweets': num_retweets,
            'Replies': num_replies
        })
    return pd.DataFrame(event_metrics)

# Function to count the number of tweets per category
def tweets_per_category(G):
    categories = [data.get('id') for node, data in G.nodes(data=True)
                 if data.get('labels') == ':PostCategory']
    tpc = []
    for category in categories:
        tweets = [source for source, target, data in G.edges(data=True)
                  if data.get('label') == 'HAS_CATEGORY' and G.nodes[target].get('id') == category]
        category_subgraph = G.subgraph(tweets)
        num_tweets = category_subgraph.number_of_nodes()
        tpc.append({
            'Category': category,
            'Number of Tweets': num_tweets,
        })
    return pd.DataFrame(tpc)

# tweets_per_category_df = tweets_per_category(G)

from collections import defaultdict

# Function to count the number of tweets per priority
def tweets_per_priority(G):
    priority_nodes = defaultdict(list)
    for node, data in G.nodes(data=True):
        if 'labels' in data and data['labels'] == ':Tweet':
            priority = data.get('annotation_postPriority', 'Unknown')
            priority_nodes[priority].append(node)
    priority_counts = {priority: len(nodes_list) for priority, nodes_list in priority_nodes.items()}
    return priority_counts

# priority_counts = tweets_per_priority(G)
# priority_counts_df = pd.DataFrame(priority_counts.items(), columns=['Priority', 'Count'])
  
# Get total number of tweets, users and hashtags

# tweet_nodes = [
#     node 
#     for node, data in G.nodes(data=True) 
#     if data.get("labels") == ":Tweet"
# ]

# user_nodes = [
#     node 
#     for node, data in G.nodes(data=True) 
#     if data.get("labels") == ":User"
# ]

# hashtag_nodes = [
#     node 
#     for node, data in G.nodes(data=True) 
#     if data.get("labels") == ":Hashtag"
# ]

# num_tweets = len(tweet_nodes)
# num_users = len(user_nodes)
# num_hashtags = len(hashtag_nodes)

# Get top 10 users for diffferent metrics
"""We define dataframes based on past calculation as recalculation would be too long"""

top_10_ressemble_info = {
    'user': ['The Associated Press', 'CNN Breaking News', 'CNN', 'Donald J. Trump',
 'NBC News', 'ABS-CBN News Channel', 'Reuters Top News', 'Narendra Modi', 'The Denver Post','Fox News'],
    'degree_centrality': [
        0.012072, 0.010460, 0.009865, 0.009825, 0.008481,
        0.007487, 0.007190, 0.006183, 0.005833, 0.005750
    ]
}

top_10_ressemble_info_df = pd.DataFrame(top_10_ressemble_info)

top_10_connect_user = {
    'user': ['Breaking News', 'CNN','NSW RFS','American Red Cross','Global Edmonton',
 'Impact Your World','USA TODAY','Naheed Nenshi','Harry Styles.','Queensland Police'],
    'betweenness_centrality': [
        4.666220e-06, 3.459798e-06, 1.040019e-06, 9.637512e-07,
        9.429508e-07, 8.805497e-07, 8.181485e-07, 5.962777e-07,
        5.754774e-07, 5.408100e-07
    ]
}

top_10_connect_user_df = pd.DataFrame(top_10_connect_user)


top_10_diffuse_info = {
    'user': ['Scooterissima??','l e x ?','Betty','Bee','gail simmons','Warren Kinsella',
 'idalis','Able Archer','Nine News Gold Coast','???championsdumonde???'],
    'nombre_de_fois_retweete': [
        12, 6, 4, 4, 4, 3, 3, 3, 3, 3
    ]
}

top_10_diffuse_info_df = pd.DataFrame(top_10_diffuse_info)

# # Count the number of interactions between users

# from collections import Counter

# # Types d'interactions à analyser
# user_interact_type = ["RETWEETS", "REPLIED_TO", "MENTIONS"]

# # Comptage des types d'interactions entre utilisateurs
# edge_type_counts = Counter()
# for interact_type in user_interact_type:
#     edge_with_type = [(u, v) for u, v, data in G.edges(data=True) if data.get('label') == interact_type]
#     edge_type_counts[interact_type] = len(edge_with_type)

# edge_type_counts["Retweets"] = edge_type_counts.pop("RETWEETS")
# edge_type_counts["Replies"] = edge_type_counts.pop("REPLIED_TO")
# edge_type_counts["Mentions"] = edge_type_counts.pop("MENTIONS")

# # Créer un DataFrame pour la visualisation
# edge_type_df = pd.DataFrame({
#     'Type of interaction': list(edge_type_counts.keys()),
#     'Number of interactions': list(edge_type_counts.values())
# })

# # Count user activity

# user_activity = {}

# for node, data in G.nodes(data=True):
#     if data.get('labels') == ':User':
#         user_id = data.get('name')
#         tweets = 0
#         retweets = 0
#         replies = 0

#         # Comptage des tweets postés par l'utilisateur
#         tweets = sum(1 for _, _, edge_data in G.edges(node, data=True) if edge_data.get('label') == 'POSTED')

#         # Comptage des retweets postés par l'utilisateur
#         retweets = sum(1 for _, _, edge_data in G.edges(node, data=True) if edge_data.get('label') == 'RETWEETS')

#         # Comptage des réponses postées par l'utilisateur
#         replies = sum(1 for _, _, edge_data in G.edges(node, data=True) if edge_data.get('label') == 'REPLIED_TO')

#         # Stockage des résultats
#         user_activity[user_id] = {
#             'Tweets': tweets,
#             'Retweets': retweets,
#             'Replies': replies,
#             'Total': tweets + retweets + replies
#         }

# user_activity_df = pd.DataFrame.from_dict(user_activity, orient='index').reset_index()
# user_activity_df.rename(columns={'index': 'User'}, inplace=True)