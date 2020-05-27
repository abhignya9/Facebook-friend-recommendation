# -*- coding: utf-8 -*-
import random
import networkx as nx
import matplotlib.pyplot as plt
from operator import itemgetter

G2 = nx.read_edgelist('Facebook_Dataset.txt', create_using = nx.Graph(), nodetype = int)

#return the friends of a user
def friends(graph, user):
    return set(graph.neighbors(user))

#returns a list of friends of friends of a user
def friends_of_friends(graph, user):
    x=[]
    for each in graph.neighbors(user):
        for item in graph.neighbors(each):
            x.append(item)
    return set(x)

# returns a list of common friends  
def common_friends(graph, user1, user2):
    x1 = friends(graph, user1)
    x2 = friends(graph, user2)
    return set(x1&x2)
    
#for each friend of a user, return a list of common friends between the user and the friend
def number_of_common_friends_map(graph, user):
    new_dict = dict()
    for each in graph.nodes():
        if(each!=user):
            if(each not in graph.neighbors(user)):
                new_dict[each] = len(common_friends(graph,each,user))
    return new_dict

#sorts the dictionary by values
def number_map_to_sorted_list(map):
    map = sorted(map.items(), key = itemgetter(1), reverse=True)
    return map

#suggest friends based on number of common friends
def recommend_by_number_of_common_friends(graph, user):
  
    diction = dict()
    diction = number_of_common_friends_map(graph,user)
    diction = number_map_to_sorted_list(diction)
    recommendations = []
    for i in range(0,10):
        recommendations.append(diction[i])
    return recommendations

#calculate the influential score for each friend
def calc_score(graph, user, each):
    score = 0
    common = common_friends(graph, user, each)
    for item in common:
        score = score + 1/(len(friends(graph, item)))
    return score
    
#returns a list of influential scores of the friends   
def influence_map(graph, user):
    influence_scores = dict()
    for each in graph.nodes():
        if(each != user):
            score = calc_score(graph, user, each)
            influence_scores[each] = score
    return influence_scores
    
#suggest friends based on the influence scores.
def recommend_by_influence(graph, user):
    recommendations = []
    d=influence_map(graph,user)
    d = number_map_to_sorted_list(d)
    for i in range(0,10):
        recommendations.append(d[i])
    return recommendations

#from the list of (recommendations,score/numberof common friends), just keep the user ID
def return_pure_list(recommendations):
    pure_list = []
    for each in recommendations:
        pure_list.append(each[0])
    return pure_list


#calculate the rank of the recommendations given by both the methods.
#lesser the better!
def compute_avg_rank(G):
    avg=0
    AVG=0
    l=[]
    f1, f2 = 0,0
    for i in range(0,1000):
        lst_of_nodes = list(G.nodes())
        f1 = random.choice(lst_of_nodes)
        f2 = random.choice(lst_of_nodes)
        if(f1!=f2):
            if(G.has_edge(f1,f2)):
                G.remove_edge(f1,f2)
                l1 = recommend_by_number_of_common_friends(G,f1)
                l2 = recommend_by_number_of_common_friends(G,f2)
                L1 = recommend_by_influence(G,f1)
                L2 = recommend_by_influence(G,f2)
                if f1 in return_pure_list(l2) and f2 in return_pure_list(l1):
                    r1 = return_pure_list(l2).index(f1)
                    r2 = return_pure_list(l1).index(f2)
                    avg=avg+(r1+r2)/2
                if f1 in return_pure_list(L2) and f2 in return_pure_list(L1):
                    R1 = return_pure_list(L2).index(f1)
                    R2 = return_pure_list(L1).index(f2)
                    AVG=AVG+(R1+R2)/2
        G.add_edge(f1,f2)
    l.append(avg)
    l.append(AVG)
    print("Average Rank of Method 1 - Recommendation by Number of Common friends: ")
    print(l[0])
    print("Average rank of Method 2 - Recommendation by influence: ")
    print(l[1])
    return l


#find the number of same and different recommendations using both methods.
def same_and_different_recommendations(graph):
    res=[]
    count_same, count_diff = 0,0
    for i in range(0,4039):
        l1,l2 = [], []
        l1 = return_pure_list(recommend_by_number_of_common_friends(graph, i))
        l2 = return_pure_list(recommend_by_influence(graph, i))
        if(l1 == l2):
            count_same = count_same + 1
        else:
            count_diff = count_diff +1
    res.append(count_same)
    res.append(count_diff)
    print("Number of Same recommendations from both methods: ")
    print(res[0])
    print("Number of different recommendations from both methods: ")
    print(res[1])
    return res
 
#return the value that occurs maximum number of times    
def most_common(lst):
    return max(set(lst), key=lst.count)


#returns a list of lonely nodes i.e. that which are not good recommendations for any user in the dataset
#Here, since we are finding the top 10 recommendations only, we are considering the last recommended friend 
#finding the lonely nodes.
def predict_lonely_nodes(graph):
    res_2=[]
    alones=[]
    for i in range(0,graph.number_of_nodes()):
        l_2 = return_pure_list(recommend_by_influence(graph,i))
        res_2.append(l_2[9])
    print("Lonely Nodes: ")
    for i in range(0,10):
        lonely = most_common(res_2)
        alones.append(lonely)
        res_2.remove(lonely)
    new_dict = dict()
    for i in range(0,10):
        new_dict[alones[i]] = nx.clustering(graph, alones[i])
    print(new_dict)
    return alones
    
#plot the nodes recommended based on the influence score
def show(graph, user):
    nx.draw_networkx_nodes(graph,pos=nx.spring_layout(graph),
                           nodelist=return_pure_list(recommend_by_influence(graph,user)),
                           node_color='b',
                           node_size=300,
                           alpha=0.5)
    plt.savefig('x.pdf')
    print("Recommendation by Influence method: " )
    print(recommend_by_influence(graph, user))
    print("*************************************************************************************")
    print("Recommendation by number of Common Friends method: ")
    print(recommend_by_number_of_common_friends(graph, user))
    

show(G2,2)     #plot the recommended users for the user specified
compute_avg_rank(G2)     #compute average ranks of both the recommendation methods
same_and_different_recommendations(G2)   #find the same and different recommendation from both methods
predict_lonely_nodes(G2)       
