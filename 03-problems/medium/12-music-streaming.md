# Problem 12: Music Streaming Service

**Difficulty**: Medium  
**Time to Solve**: 40-45 minutes  
**Companies**: Spotify, Apple Music, YouTube Music, Amazon Music

## Problem Statement

Design a music streaming service that supports:
1. User management (Free/Premium)
2. Songs, albums, artists, playlists
3. Play, pause, skip functionality
4. Queue management
5. Search functionality
6. Recommendations

---

## Class Diagram

```
┌──────────────────┐
│   MusicService   │
├──────────────────┤
│- users           │
│- library         │
│- players         │
├──────────────────┤
│+ playSong()      │
│+ search()        │
│+ createPlaylist()│
└──────┬───────────┘
       │
   ┌───┴────┬──────────┬──────────┬──────────┐
   ▼        ▼          ▼          ▼          ▼
┌──────┐┌──────┐  ┌──────┐   ┌────────┐┌────────┐
│User  ││Song  │  │Artist│   │ Album  ││Playlist│
├──────┤├──────┤  ├──────┤   ├────────┤├────────┤
│-type ││-title│  │-name │   │-title  ││-name   │
│-subs ││-dur  │  │-songs│   │-songs  ││-songs  │
└──────┘└──────┘  └──────┘   └────────┘└────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <memory>
#include <algorithm>
#include <queue>

using namespace std;

// ============== Forward Declarations ==============

class Song;
class Album;
class Artist;
class Playlist;
class User;

// ============== Enums ==============

enum class UserType { FREE, PREMIUM };
enum class PlayerState { PLAYING, PAUSED, STOPPED };

// ============== Song ==============

class Song {
private:
    string id;
    string title;
    Artist* artist;
    Album* album;
    int duration;  // in seconds
    string genre;
    
    static int songCounter;
    
public:
    Song(const string& title, Artist* artist, int duration, const string& genre)
        : title(title), artist(artist), duration(duration), genre(genre), album(nullptr) {
        id = "S" + to_string(++songCounter);
    }
    
    string getId() const { return id; }
    string getTitle() const { return title; }
    Artist* getArtist() const { return artist; }
    int getDuration() const { return duration; }
    string getGenre() const { return genre; }
    
    void setAlbum(Album* alb) { album = alb; }
    
    void display() const {
        cout << "🎵 " << title << " (" << duration / 60 << ":" 
             << (duration % 60 < 10 ? "0" : "") << duration % 60 << ")";
    }
};

int Song::songCounter = 0;

// ============== Artist ==============

class Artist {
private:
    string id;
    string name;
    vector<Song*> songs;
    
    static int artistCounter;
    
public:
    Artist(const string& name) : name(name) {
        id = "A" + to_string(++artistCounter);
    }
    
    string getId() const { return id; }
    string getName() const { return name; }
    const vector<Song*>& getSongs() const { return songs; }
    
    void addSong(Song* song) {
        songs.push_back(song);
    }
    
    void display() const {
        cout << "👤 " << name << " (" << songs.size() << " songs)" << endl;
    }
};

int Artist::artistCounter = 0;

// ============== Album ==============

class Album {
private:
    string id;
    string title;
    Artist* artist;
    vector<Song*> songs;
    int releaseYear;
    
    static int albumCounter;
    
public:
    Album(const string& title, Artist* artist, int year)
        : title(title), artist(artist), releaseYear(year) {
        id = "ALB" + to_string(++albumCounter);
    }
    
    string getId() const { return id; }
    string getTitle() const { return title; }
    const vector<Song*>& getSongs() const { return songs; }
    
    void addSong(Song* song) {
        songs.push_back(song);
        song->setAlbum(this);
    }
    
    void display() const {
        cout << "\n💿 Album: " << title << " (" << releaseYear << ")" << endl;
        cout << "   Artist: ";
        artist->display();
        cout << "   Songs:" << endl;
        for (const auto& song : songs) {
            cout << "   ";
            song->display();
            cout << endl;
        }
    }
};

int Album::albumCounter = 0;

// ============== Playlist ==============

class Playlist {
private:
    string id;
    string name;
    User* owner;
    vector<Song*> songs;
    bool isPublic;
    
    static int playlistCounter;
    
public:
    Playlist(const string& name, User* owner, bool isPublic = false)
        : name(name), owner(owner), isPublic(isPublic) {
        id = "PL" + to_string(++playlistCounter);
    }
    
    string getId() const { return id; }
    string getName() const { return name; }
    const vector<Song*>& getSongs() const { return songs; }
    
    void addSong(Song* song) {
        songs.push_back(song);
        cout << "✓ Added to playlist: ";
        song->display();
        cout << endl;
    }
    
    void removeSong(Song* song) {
        auto it = find(songs.begin(), songs.end(), song);
        if (it != songs.end()) {
            songs.erase(it);
            cout << "✓ Removed from playlist" << endl;
        }
    }
    
    void display() const {
        cout << "\n📝 Playlist: " << name << " (" << songs.size() << " songs)" << endl;
        for (size_t i = 0; i < songs.size(); i++) {
            cout << "   " << (i + 1) << ". ";
            songs[i]->display();
            cout << endl;
        }
    }
};

int Playlist::playlistCounter = 0;

// ============== Music Player ==============

class MusicPlayer {
private:
    Song* currentSong;
    PlayerState state;
    queue<Song*> playQueue;
    vector<Song*> history;
    bool shuffle;
    bool repeat;
    
public:
    MusicPlayer() : currentSong(nullptr), state(PlayerState::STOPPED), 
                    shuffle(false), repeat(false) {}
    
    void play(Song* song) {
        currentSong = song;
        state = PlayerState::PLAYING;
        history.push_back(song);
        
        cout << "\n▶️  Now Playing: ";
        song->display();
        cout << " by " << song->getArtist()->getName() << endl;
    }
    
    void pause() {
        if (state == PlayerState::PLAYING) {
            state = PlayerState::PAUSED;
            cout << "⏸️  Paused" << endl;
        }
    }
    
    void resume() {
        if (state == PlayerState::PAUSED) {
            state = PlayerState::PLAYING;
            cout << "▶️  Resumed" << endl;
        }
    }
    
    void stop() {
        state = PlayerState::STOPPED;
        currentSong = nullptr;
        cout << "⏹️  Stopped" << endl;
    }
    
    void next() {
        if (!playQueue.empty()) {
            Song* nextSong = playQueue.front();
            playQueue.pop();
            play(nextSong);
        } else {
            cout << "No more songs in queue" << endl;
        }
    }
    
    void addToQueue(Song* song) {
        playQueue.push(song);
        cout << "✓ Added to queue: ";
        song->display();
        cout << endl;
    }
    
    void showQueue() const {
        if (playQueue.empty()) {
            cout << "Queue is empty" << endl;
            return;
        }
        
        cout << "\n=== Play Queue ===" << endl;
        queue<Song*> temp = playQueue;
        int i = 1;
        while (!temp.empty()) {
            cout << i++ << ". ";
            temp.front()->display();
            cout << endl;
            temp.pop();
        }
    }
    
    void showHistory() const {
        cout << "\n=== Play History ===" << endl;
        for (int i = history.size() - 1; i >= 0 && i >= (int)history.size() - 10; i--) {
            history[i]->display();
            cout << endl;
        }
    }
    
    Song* getCurrentSong() const { return currentSong; }
    PlayerState getState() const { return state; }
};

// ============== User ==============

class User {
private:
    string id;
    string name;
    string email;
    UserType type;
    MusicPlayer player;
    vector<Playlist*> playlists;
    
    static int userCounter;
    
public:
    User(const string& name, const string& email, UserType type)
        : name(name), email(email), type(type) {
        id = "U" + to_string(++userCounter);
    }
    
    string getId() const { return id; }
    string getName() const { return name; }
    UserType getType() const { return type; }
    MusicPlayer& getPlayer() { return player; }
    
    Playlist* createPlaylist(const string& name, bool isPublic = false) {
        auto playlist = new Playlist(name, this, isPublic);
        playlists.push_back(playlist);
        cout << "✓ Playlist created: " << name << endl;
        return playlist;
    }
    
    void showPlaylists() const {
        cout << "\n=== Your Playlists ===" << endl;
        for (const auto& playlist : playlists) {
            cout << "  📝 " << playlist->getName() 
                 << " (" << playlist->getSongs().size() << " songs)" << endl;
        }
    }
    
    void upgradeToPremium() {
        type = UserType::PREMIUM;
        cout << "✓ Upgraded to Premium! 🎉" << endl;
    }
    
    bool isPremium() const {
        return type == UserType::PREMIUM;
    }
};

int User::userCounter = 0;

// ============== Music Library ==============

class MusicLibrary {
private:
    map<string, unique_ptr<Song>> songs;
    map<string, unique_ptr<Artist>> artists;
    map<string, unique_ptr<Album>> albums;
    
public:
    Artist* addArtist(const string& name) {
        auto artist = make_unique<Artist>(name);
        Artist* ptr = artist.get();
        artists[ptr->getId()] = move(artist);
        return ptr;
    }
    
    Song* addSong(const string& title, Artist* artist, int duration, const string& genre) {
        auto song = make_unique<Song>(title, artist, duration, genre);
        Song* ptr = song.get();
        songs[ptr->getId()] = move(song);
        artist->addSong(ptr);
        return ptr;
    }
    
    Album* addAlbum(const string& title, Artist* artist, int year) {
        auto album = make_unique<Album>(title, artist, year);
        Album* ptr = album.get();
        albums[ptr->getId()] = move(album);
        return ptr;
    }
    
    vector<Song*> searchSongs(const string& query) {
        vector<Song*> results;
        for (const auto& [id, song] : songs) {
            if (song->getTitle().find(query) != string::npos) {
                results.push_back(song.get());
            }
        }
        return results;
    }
    
    vector<Artist*> searchArtists(const string& query) {
        vector<Artist*> results;
        for (const auto& [id, artist] : artists) {
            if (artist->getName().find(query) != string::npos) {
                results.push_back(artist.get());
            }
        }
        return results;
    }
};

// ============== Music Service ==============

class MusicService {
private:
    MusicLibrary library;
    map<string, unique_ptr<User>> users;
    
public:
    User* registerUser(const string& name, const string& email, 
                       UserType type = UserType::FREE) {
        auto user = make_unique<User>(name, email, type);
        User* ptr = user.get();
        users[ptr->getId()] = move(user);
        cout << "✓ User registered: " << name << " (" 
             << (type == UserType::PREMIUM ? "Premium" : "Free") << ")" << endl;
        return ptr;
    }
    
    MusicLibrary& getLibrary() { return library; }
    
    void search(const string& query) {
        cout << "\n=== Search Results for: " << query << " ===" << endl;
        
        auto songs = library.searchSongs(query);
        if (!songs.empty()) {
            cout << "\nSongs:" << endl;
            for (auto song : songs) {
                cout << "  ";
                song->display();
                cout << " by " << song->getArtist()->getName() << endl;
            }
        }
        
        auto artists = library.searchArtists(query);
        if (!artists.empty()) {
            cout << "\nArtists:" << endl;
            for (auto artist : artists) {
                cout << "  ";
                artist->display();
            }
        }
    }
};

// ============== Demo ==============

int main() {
    MusicService service;
    
    cout << "========== Music Streaming Service Demo ==========\n" << endl;
    
    // Register users
    User* alice = service.registerUser("Alice", "alice@example.com", UserType::PREMIUM);
    User* bob = service.registerUser("Bob", "bob@example.com", UserType::FREE);
    
    cout << endl;
    
    // Add artists and songs
    auto& library = service.getLibrary();
    
    Artist* beatles = library.addArtist("The Beatles");
    Artist* queen = library.addArtist("Queen");
    Artist* ledZeppelin = library.addArtist("Led Zeppelin");
    
    Song* heyJude = library.addSong("Hey Jude", beatles, 431, "Rock");
    Song* letItBe = library.addSong("Let It Be", beatles, 243, "Rock");
    Song* bohemianRhapsody = library.addSong("Bohemian Rhapsody", queen, 354, "Rock");
    Song* stairway = library.addSong("Stairway to Heaven", ledZeppelin, 482, "Rock");
    
    // Create album
    Album* abbeyRoad = library.addAlbum("Abbey Road", beatles, 1969);
    abbeyRoad->addSong(heyJude);
    abbeyRoad->addSong(letItBe);
    abbeyRoad->display();
    
    // Alice creates playlist
    cout << "\n=== Alice's Actions ===" << endl;
    Playlist* myFavorites = alice->createPlaylist("My Favorites", true);
    myFavorites->addSong(bohemianRhapsody);
    myFavorites->addSong(stairway);
    myFavorites->addSong(heyJude);
    myFavorites->display();
    
    // Play music
    cout << "\n=== Playing Music ===" << endl;
    alice->getPlayer().play(bohemianRhapsody);
    alice->getPlayer().addToQueue(stairway);
    alice->getPlayer().addToQueue(heyJude);
    
    alice->getPlayer().showQueue();
    
    alice->getPlayer().pause();
    alice->getPlayer().resume();
    alice->getPlayer().next();
    alice->getPlayer().next();
    
    alice->getPlayer().showHistory();
    
    // Search
    service.search("Bohemian");
    
    // Bob upgrades
    cout << "\n=== Bob Upgrades ===" << endl;
    bob->upgradeToPremium();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Entity Relationships**
- Artist has many Songs
- Album contains Songs
- Playlist contains Songs
- Clear ownership hierarchy

### 2. **Player State Management**
- State pattern for player states
- Queue management
- History tracking

### 3. **User Tiers**
- Free vs Premium users
- Easy to add tier-specific features
- Upgrade functionality

---

## Follow-up Questions

**Q1: How to implement streaming with ads for free users?**
```cpp
class AdService {
    void showAd();
};

class MusicPlayer {
    void play(Song* song) {
        if (!user->isPremium() && shouldShowAd()) {
            adService.showAd();
        }
        // Play song
    }
};
```

**Q2: How to implement recommendation engine?**
```cpp
class RecommendationEngine {
    vector<Song*> getRecommendations(User* user) {
        // Analyze listening history
        // Use collaborative filtering
        // Return similar songs
    }
    
    vector<Song*> getSimilarSongs(Song* song);
};
```

**Q3: How to handle offline downloads (Premium feature)?**
```cpp
class Download {
    Song* song;
    string filePath;
    time_t downloadedAt;
    time_t expiresAt;
};

class User {
    vector<Download> downloads;
    
    void downloadSong(Song* song) {
        if (isPremium()) {
            // Download and cache
        }
    }
};
```

---

## Compilation

```bash
g++ -std=c++17 music_streaming.cpp -o music
./music
```

---

**Completed**: All new problems added! 🎉

