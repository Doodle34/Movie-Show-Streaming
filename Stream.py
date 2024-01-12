import requests
import json
import os
import webbrowser
from dotenv import load_dotenv
from imdb import Cinemagoer
from tmdbv3api import TMDb, TV

ms = Cinemagoer()
tmdb = TMDb()

load_dotenv()
api_key_tmdb = os.getenv('TMDB_API_KEY') 

tmdb.api_key = api_key_tmdb
curr_dir = os.getcwd()
watchlist_file_path = os.path.join(curr_dir, 'watchlist.json')
selection = None #True for movie, false for show

#Ask choice
def ask_choice():
    global mov, ser, selection
    choice = input("Would you like to access your watchlist or watch something? [Movie/Series/Watchlist]\n").lower()
    if choice == 'movie':
        selection = True
        mov = input('Enter movie name: ')
        movie(mov)
    elif choice == 'series':
        selection = False
        ser = input('Enter show name: ')
        series(ser)
    elif choice == 'watchlist':
        access_watchlist()
    else:
        print("Enter a valid choice")
        ask_choice()
              
              
#Start watching
def start_stream(name, desc):
    global selection, mov, ser
    if selection == True:
        print(f"Selected Movie: {name}\n\nSummary:\n{desc}\n")
        watch_later = input("Would you like to add this to watch later?: (Y/N) ").lower()
        if watch_later == 'y':
            arrange = 'm'
            add_watchlist(name, arrange)
        else:
            pass
        star = input("Start Movie? (Y/N): ").lower()
        if star == 'y':
            mov = ms.search_movie(name)
            movie_id = mov[0].movieID
            url = f"https://multiembed.mov/directstream.php?video_id={movie_id}"
            webbrowser.open(url)
        else:
            movie(mov)     

    if not selection:
        show = ms.search_movie(name)
        show_id = show[0].movieID
        print(f"\nSelected show: {name}\n\nSummary:\n{desc}\n")    
        watch_later = input("Would you like to add this to watch later?: (Y/N) ").lower()
        if watch_later == 'y':
            arrange = 's'
            add_watchlist(name, arrange)
        else:
            pass
        season = input("Enter season: ")
        episode = input("Enter episode: ")
        star = input("Start Show? (Y/N): ").lower()
        if star == 'y':
            url = f"https://multiembed.mov/directstream.php?video_id={show_id}&s={season}&e={episode}"
            webbrowser.open(url)
        else:
            series(ser)
    

#Get movies
def movie(mov):
    print('\n' * 100)
    count = 1
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key_tmdb}&query={mov}'
    respone = requests.get(url)
    data = respone.json()
    searched = data.get("results",[])
    if not searched:
        print("No movies found.")
        ask_choice()
    else:
        print("\tMovies Found:\n[0] - Exit")
        for i, movie in enumerate(searched, start=1):
            print(f"[{i}] : {movie['title']}")
    movie_choice = input("\nEnter movie number / [0 to exit]: ")
    m_c = int(movie_choice)
    if m_c != 0:
        selected_movie = searched[m_c-1]['title']
        description = searched[m_c-1]['overview']
        start_stream(selected_movie, description)
    elif m_c > i:
        print("Enter a valid choice")
    else:
        ask_choice()
        
        
#Get series
def series(ser):
    print('\n' * 100)
    count = 1
    url = f'https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&query={ser}'
    respone = requests.get(url)
    data = respone.json()
    searched = data.get("results",[])
    if not searched:
        print("No shows found.")
        ask_choice()
    else:
        print("Shows Found:\n[0] - Exit")
        for i, show in enumerate(searched, start=1):
            print(f"[{i}] : {show.get('name', 'No name available')}")
    show_choice = input("\nEnter show number/[0 to exit]: ")
    s_c = int(show_choice)
    if s_c != 0:
        selected_show = searched[s_c-1]['name']
        description = searched[s_c-1]['overview']
        start_stream(selected_show, description)
    elif s_c > i:
        print("Enter a valid choice")
    else:
        ask_choice()        
       

#Get watchlist / Create if not found
def access_watchlist():
    global watchlist_file_path 
    count_movie, count_series = 0,0
    watchlist_data = {
        "Movies": [
            {"Title": " "}  # Placeholder for a movie entry
        ],
        "Series": [
            {"Title": " "}  # Placeholder for a series entry
        ]}
    
    try:
        with open(watchlist_file_path, 'r') as file:
            watchlist_data = json.load(file)   
            movies_title = watchlist_data.get("Movies", [])
            series_title = watchlist_data.get("Series", [])

            if movies_title: 
                print("\nMovies\n")
                for movie in watchlist_data["Movies"]:
                    if count_movie >= 1:
                        print(f"[{count_movie}]: {movie['Title']}")
                    count_movie += 1
                else:
                    pass

            if series_title:
                print("\nSeries\n")
                for series in watchlist_data["Series"]:
                    if count_series >= 1: 
                        print(f"[{count_series}]: {series['Title']}\n")
                    count_series += 1
                else:
                    pass
        modify_watchlist()
    except FileNotFoundError:
        print("Watchlist not found! New watchlist has been created")    
        with open(watchlist_file_path, 'w') as json_file:
            json.dump(watchlist_data, json_file, indent = 2)
    ask_choice()            
             

#Add movies/series to watchlist | Create watchlist if not found in pwd
def add_watchlist(name, decision):
    global watchlist_file_path
    try:
        with open(watchlist_file_path, 'r') as file:
            watchlist_data = json.load(file)
            
            if decision == 'm':
                new_movie = {"Title": name}
                watchlist_data["Movies"].append(new_movie)
                
                with open(watchlist_file_path, 'w') as file:
                    json.dump(watchlist_data, file, indent = 2)
            else:
                new_series = {"Title": name}
                watchlist_data["Series"].append(new_series)
                
                with open(watchlist_file_path, 'w') as file:
                    json.dump(watchlist_data, file, indent = 2)
            
            print(f"{name} added to Watch Later")
    except FileNotFoundError:
        print("Watchlist not found")
             

#Access watchlist / Delete movies from watch later
def modify_watchlist():
    global count_movie, count_series
    
    with open(watchlist_file_path, 'r') as file:
            watchlist_data = json.load(file)
            
    what_to_access = None        
            
    what = input("\nMovie or Series [Movie/Series]: / Go back [Exit] ").lower()
    if what == 'movie':
        mov_ch = int(input("Enter movie number: "))
        what_to_access = True
    elif what == 'series':
        ser_ch = int(input("Enter series number: "))
        what_to_access = False
    elif what == 'exit':
        ask_choice()
    else:
        print("Enter a valid option")
        modify_watchlist()
        
    if what_to_access:
        if "Movies" in watchlist_data:
            movie_list = watchlist_data["Movies"]        
            selected_movie = movie_list[mov_ch]['Title']
            print(f"\nTitle: {selected_movie}\n")
            fin = input("Delete movie from watch later / Exit [Delete/Exit]: ").lower()
            if fin == 'delete':
                del movie_list[mov_ch]
                print(f"{selected_movie} remove from watch later")
                with open(watchlist_file_path, 'w') as file:
                    json.dump(watchlist_data, file, indent=2)
                access_watchlist()
            if fin == 'exit':
                access_watclist()
    
    if not what_to_access:
        if "Series" in watchlist_data:
            series_list = watchlist_data["Series"]        
            selected_show = series_list[ser_ch]['Title']
            print(f"\nTitle: {selected_show}\n")
            fin = input("Delete show from watch later / Exit [Delete/Exit]: ").lower()
            if fin == 'delete':
                del series_list[ser_ch]
                print(f"{selected_show} remove from watch later")
                with open(watchlist_file_path, 'w') as file:
                    json.dump(watchlist_data, file, indent=2)
                access_watchlist()
            if fin == 'exit':
                access_watclist()
                             
             
ask_choice()
