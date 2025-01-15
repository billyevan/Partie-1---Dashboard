import streamlit as st
from utils import * # Import all functions from the utils.py file
import networkx as nx
import pandas as pd
import plotly.express as px

# This script is used to create the dashboard for the Crisis Events project using Streamlit

st.set_page_config(page_title="Dashboard | Crisis Events", page_icon=":bar_chart:", layout="wide") 

st.title(":red[Data Dashboard] for :orange[Crisis Events] in :blue[Social Media]")
st.write("This is a dashboard to analyze crisis events on Twitter (now X). The data is collected from TREC.")
st.write("Made with ❤️ by Mamady Djiguiném | Evandion Kurniadi | Bernadette Babagnak")
url = "https://drive.google.com/file/d/17RakKWgDPRv8GsmzySM9iF6toCS2v1Ew/view?usp=sharing"
st.write("Download the dataset [here](%s)!" % url)

uploaded_file = st.file_uploader("Choose a file", type=['graphml'], accept_multiple_files=False)
if uploaded_file is not None:
    G = nx.read_graphml(uploaded_file)
    # Key figures to describe the data

    tweets_per_category_df = tweets_per_category(G)
    priority_counts = tweets_per_priority(G)
    priority_counts_df = pd.DataFrame(priority_counts.items(), columns=['Priority', 'Count'])

    tweet_nodes = [
        node 
        for node, data in G.nodes(data=True) 
        if data.get("labels") == ":Tweet"
    ]

    user_nodes = [
        node 
        for node, data in G.nodes(data=True) 
        if data.get("labels") == ":User"
    ]

    hashtag_nodes = [
        node 
        for node, data in G.nodes(data=True) 
        if data.get("labels") == ":Hashtag"
    ]

    num_tweets = len(tweet_nodes)
    num_users = len(user_nodes)
    num_hashtags = len(hashtag_nodes)

    # Count the number of interactions between users

    from collections import Counter

    # Types d'interactions à analyser
    user_interact_type = ["RETWEETS", "REPLIED_TO", "MENTIONS"]

    # Comptage des types d'interactions entre utilisateurs
    edge_type_counts = Counter()
    for interact_type in user_interact_type:
        edge_with_type = [(u, v) for u, v, data in G.edges(data=True) if data.get('label') == interact_type]
        edge_type_counts[interact_type] = len(edge_with_type)

    edge_type_counts["Retweets"] = edge_type_counts.pop("RETWEETS")
    edge_type_counts["Replies"] = edge_type_counts.pop("REPLIED_TO")
    edge_type_counts["Mentions"] = edge_type_counts.pop("MENTIONS")

    # Créer un DataFrame pour la visualisation
    edge_type_df = pd.DataFrame({
        'Type of interaction': list(edge_type_counts.keys()),
        'Number of interactions': list(edge_type_counts.values())
    })

    # Count user activity

    user_activity = {}

    for node, data in G.nodes(data=True):
        if data.get('labels') == ':User':
            user_id = data.get('name')
            tweets = 0
            retweets = 0
            replies = 0

            # Comptage des tweets postés par l'utilisateur
            tweets = sum(1 for _, _, edge_data in G.edges(node, data=True) if edge_data.get('label') == 'POSTED')

            # Comptage des retweets postés par l'utilisateur
            retweets = sum(1 for _, _, edge_data in G.edges(node, data=True) if edge_data.get('label') == 'RETWEETS')

            # Comptage des réponses postées par l'utilisateur
            replies = sum(1 for _, _, edge_data in G.edges(node, data=True) if edge_data.get('label') == 'REPLIED_TO')

            # Stockage des résultats
            user_activity[user_id] = {
                'Tweets': tweets,
                'Retweets': retweets,
                'Replies': replies,
                'Total': tweets + retweets + replies
            }

    user_activity_df = pd.DataFrame.from_dict(user_activity, orient='index').reset_index()
    user_activity_df.rename(columns={'index': 'User'}, inplace=True)

    # Dashboard visuals start here

    node, edges, tweets, users, hashtags = st.columns(5)
    node.metric("Number of nodes", str(G.number_of_nodes()), border=True)
    edges.metric("Number of edges", str(G.number_of_edges()), border=True)
    tweets.metric("Number of tweets", str(num_tweets), border=True)
    users.metric("Number of users", str(num_users), border=True)
    hashtags.metric("Number of hashtags", str(num_hashtags), border=True)

    # Divide in columns
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        with st.container(border=True):
            st.markdown("#### Interaction between users")
            st.bar_chart(edge_type_df, x="Type of interaction", y="Number of interactions", horizontal=True, color="Type of interaction")
            # interaction_fig = px.bar(edge_type_df, x='Type d\'interaction', y='Nombre d\'interactions',
            #             title='Frequency of interactions between users',
            #             labels={'Type d\'interaction': 'Type of interaction', 'Nombre d\'interactions': 'Number of interactions', 'RETWEETS': 'Retweets', 'REPLY_TO': 'Replies', 'MENTIONS': 'Mentions'},
            #             text_auto=True)
            # st.plotly_chart(interaction_fig)
        
        with st.container(border=True):
            st.markdown("### Tweet priority")
            st.bar_chart(priority_counts_df, x='Priority', y='Count', horizontal=True, color='Priority')
        
        with st.container(border=True):
            st.markdown("### Tweet category")
            st.bar_chart(tweets_per_category_df, y='Number of Tweets', x='Category', horizontal=True)

    with col2:
        
        with st.container(border=True):
            st.markdown("### Social activities based on sub-events")
            option = st.selectbox(
                "Choose the sub-event",
                ("Flood", "Wildfire", "Earthquake", "Shooting", "Bombing", "Typhoon")
            )
            metrics_df = mesure_activity_intensity(G, option.lower())
            st.markdown(f'''##### Social activity for {option.lower()}''')
            # st.bar_chart(metrics_df, x='Event ID', y=['Tweets', 'Retweets', 'Replies'])

            fig = px.bar(metrics_df, x='Event ID', y=['Tweets', 'Retweets', 'Replies'],
                            #title=f"Social activity for {option.lower()}",
                            labels={'value': "Number of activities", 'variable': 'Metric', 'Event ID': 'Even'},
                            barmode='group',text_auto=True)
            st.plotly_chart(fig)

        
        with st.container(border=True):
            st.markdown("### Time trends in social activities")
            event_types = set(data.get('eventType') for node, data in G.nodes(data=True) if data.get('labels') == ':Event')
            option2 = st.selectbox(
                "Choose the sub-event",
                ('Bombing', 'Earthquake', 'Flood', 'Shooting', 'Typhoon', 'Wildfire')
            )

            event_ids = [data.get('id') for node, data in G.nodes(data=True) if data.get('labels') == ':Event' and data.get('eventType') == option2.lower()]
            tweets = [source for source, target, data in G.edges(data=True) if data.get('label') == 'IS_ABOUT' and G.nodes[target].get('id') in event_ids]

            tweet_dates = [data.get('created_at') for node, data in G.nodes(data=True) if node in tweets]
            tweet_dates = pd.to_datetime(tweet_dates)

            tweet_dates_df = pd.DataFrame(tweet_dates, columns=['Date'])
            tweet_dates_df['Count'] = 1
            tweet_dates_df = tweet_dates_df.resample('D', on='Date').sum().reset_index()

            st.markdown(f'''##### Number of tweets over time for {option2.lower()}''')
            # st.bar_chart(tweet_dates_df, x='Date', y='Count')

            # Visualisation l'évolution temporelle avec Plotly
            # fig2 = px.line(tweet_dates_df, x='Date', y='Count', 
            #                labels={'Count': "Nombre de tweets", 'Date': 'Date'},
            #                title=f"Évolution du nombre de tweets par jour pour l'événement {option2.lower()}")
            # col1.plotly_chart(fig2)

            fig2 = px.line(tweet_dates_df, x='Date', y='Count',
                labels={'Count': "Nombre de tweets", 'Date': 'Date'},
                #title=f"Évolution du nombre de tweets par jour pour l'événement {option2.lower()}"
            )

            # Configuration du range slider et des boutons de sélection
            fig2.update_layout(
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=7,
                                label="1 week",
                                step="day",
                                stepmode="backward"),
                            dict(count=1,
                                label="1 month",
                                step="month",
                                stepmode="backward"),
                            dict(count=6,
                                label="6 months",
                                step="month",
                                stepmode="backward"),
                            dict(count=1,
                                label="1 year",
                                step="year",
                                stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(
                        visible=True
                    ),
                    type="date"
                )
            )

            st.plotly_chart(fig2)

    with col3:    
        
        with st.container(border=True):
            st.markdown("#### Central users")
            option = st.selectbox(
                "Choose the criteria",
                ("Ability to connect users", "Ability to spread information", "Ability to gather information")
            )
            if option == "Ability to connect users":
                st.write("This metric measures the ability of a user to connect other users (i.e. to be a bridge between them) based on the Betweeness Centrality.")
                st.dataframe(top_10_connect_user_df,
                    #  column_order=("user", "betweenness_centrality"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "user": st.column_config.TextColumn(
                            "User ID",
                        ),
                        "betweenness_centrality": st.column_config.ProgressColumn(
                            "Betweenness Centrality",
                            format="%f",
                            min_value=0,
                            max_value=max(top_10_connect_user_df.betweenness_centrality),
                        )}
                    )
            elif option == "Ability to spread information":
                st.write("This metric measures the ability of a user to spread information to a (potentially) large(r) number of users, based on the number of times the user has been retweeted.")
                st.dataframe(top_10_diffuse_info_df,
                    column_order=("user", "nombre_de_fois_retweete"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "user": st.column_config.TextColumn(
                            "User ID",
                        ),
                        "nombre_de_fois_retweete": st.column_config.ProgressColumn(
                            "Number of times retweeted",
                            format="%f",
                            min_value=0,
                            max_value=max(top_10_diffuse_info_df.nombre_de_fois_retweete),
                        )}
                    )
            else:
                st.write("This metric measures the ability of a user to receive information or to be a source of information for other users based on Degree Centrality.")
                st.dataframe(top_10_ressemble_info_df,
                    column_order=("user", "degree_centrality"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "user": st.column_config.TextColumn(
                            "User ID",
                        ),
                        "degree_centrality": st.column_config.ProgressColumn(
                            "Degree Centrality",
                            format="%f",
                            min_value=0,
                            max_value=max(top_10_ressemble_info_df.degree_centrality),
                        )}
                    )
        with st.container(border=True):
            st.markdown("#### User activity")
            st.write("Click on the column name to sort the data.")
            st.write("Resize columns as you wish.")
            st.dataframe(user_activity_df)

else:
    st.stop()


# ================================ CODE DUMP ================================

# cola1, cola2, cola3, cola4 = st.columns(4)

# with cola1:

# st.markdown("#### Capacité à rassembler des informations")
# st.write("This metric measures the ability of a user to receive information or to be a source of information for other users. For this, the following relationships are used: 'POSTED', 'MENTIONS', 'REPLIED_TO'")
# col2.dataframe(top_10_ressemble_info_df,
#                  column_order=("user", "degree_centrality"),
#                  hide_index=True,
#                  width=None,
#                  column_config={
#                     "user": st.column_config.TextColumn(
#                         "User ID",
#                     ),
#                     "degree_centrality": st.column_config.ProgressColumn(
#                         "Degree Centrality",
#                         format="%f",
#                         min_value=0,
#                         max_value=max(top_10_ressemble_info_df.degree_centrality),
#                      )}
#                  )

# col2.subheader("Capacité à connecter les utilisateurs")
# col2.write("This metric measures the ability of a user to connect other users, i.e., to be a bridge between them.")
# col2.dataframe(top_10_connect_user_df,
#                 column_order=("user", "betweenness_centrality"),
#                  hide_index=True,
#                  width=None,
#                  column_config={
#                     "user": st.column_config.TextColumn(
#                         "User ID",
#                     ),
#                     "betweenness_centrality": st.column_config.ProgressColumn(
#                         "Betweenness Centrality",
#                         format="%f",
#                         min_value=0,
#                         max_value=max(top_10_connect_user_df.betweenness_centrality),
#                      )}
#                  )

# col2.subheader("Capacité à diffuser des informations")
# col2.write("This metric measures the ability of a user to spread information to a large number of users.")
# col2.dataframe(top_10_diffuse_info_df,
#                 column_order=("user", "nombre_de_fois_retweete"),
#                  hide_index=True,
#                  width=None,
#                  column_config={
#                     "user": st.column_config.TextColumn(
#                         "User ID",
#                     ),
#                     "nombre_de_fois_retweete": st.column_config.ProgressColumn(
#                         "Number of times retweeted",
#                         format="%f",
#                         min_value=0,
#                         max_value=max(top_10_diffuse_info_df.nombre_de_fois_retweete),
#                      )}
#                  )

# # ================================

# user_activity = {}

# for node, data in G.nodes(data=True):
#     if data.get('labels') == ':User':
#         user_id = node
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
#             'Total Activity': tweets + retweets + replies
#         }

# # 2. Convertion en DataFrame
# user_activity_df = pd.DataFrame.from_dict(user_activity, orient='index').reset_index()
# user_activity_df.rename(columns={'index': 'User'}, inplace=True)
