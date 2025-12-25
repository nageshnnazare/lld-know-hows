# Problem 10: Social Media Feed

**Difficulty**: Medium  
**Time to Solve**: 50-60 minutes  
**Companies**: Facebook, Twitter, Instagram, LinkedIn

## Problem Statement

Design a social media feed system that supports:
1. Create posts (text, images)
2. Follow/Unfollow users
3. Like/Comment on posts
4. Generate personalized feed
5. Trending posts
6. Hashtag support

---

## Class Diagram

```
┌─────────────────────┐
│  SocialMedia        │
├─────────────────────┤
│ - users             │
│ - posts             │
│ - feedAlgorithm     │
├─────────────────────┤
│ + createPost()      │
│ + followUser()      │
│ + generateFeed()    │
│ + getTrending()     │
└──────┬──────────────┘
       │
    ┌──┴────────────┬──────────┐
    ▼               ▼          ▼
┌──────────┐ ┌───────────┐ ┌───────────┐
│   User   │ │   Post    │ │  Comment  │
├──────────┤ ├───────────┤ ├───────────┤
│- id      │ │- id       │ │- author   │
│- name    │ │- author   │ │- text     │
│-followers│ │- likes    │ │- timestamp│
│-following│ │- comments │ │           │
│- posts   │ │- timestamp│ │           │
└──────────┘ └───────────┘ └───────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <string>
#include <algorithm>
#include <ctime>
#include <sstream>
#include <iomanip>

using namespace std;

// Forward declarations
class User;
class Post;
class Comment;

// ============== Comment ==============

class Comment {
private:
    User* author;
    string text;
    time_t timestamp;
    static int commentCounter;
    string commentId;
    
public:
    Comment(User* a, const string& t)
        : author(a), text(t), timestamp(time(nullptr)) {
        commentId = "C" + to_string(++commentCounter);
    }
    
    User* getAuthor() const { return author; }
    string getText() const { return text; }
    time_t getTimestamp() const { return timestamp; }
    
    void display() const;
};

int Comment::commentCounter = 0;

// ============== Post ==============

class Post {
private:
    string postId;
    User* author;
    string content;
    vector<string> hashtags;
    set<User*> likes;
    vector<unique_ptr<Comment>> comments;
    time_t timestamp;
    static int postCounter;
    
public:
    Post(User* a, const string& content);
    
    string getId() const { return postId; }
    User* getAuthor() const { return author; }
    string getContent() const { return content; }
    time_t getTimestamp() const { return timestamp; }
    
    const vector<string>& getHashtags() const { return hashtags; }
    
    void like(User* user) {
        likes.insert(user);
    }
    
    void unlike(User* user) {
        likes.erase(user);
    }
    
    bool isLikedBy(User* user) const {
        return likes.find(user) != likes.end();
    }
    
    int getLikeCount() const {
        return likes.size();
    }
    
    void addComment(User* user, const string& text) {
        comments.push_back(make_unique<Comment>(user, text));
    }
    
    int getCommentCount() const {
        return comments.size();
    }
    
    // Engagement score for trending calculation
    double getEngagementScore() const {
        double currentTime = time(nullptr);
        double ageInHours = (currentTime - timestamp) / 3600.0;
        
        // Decay over time
        double decayFactor = 1.0 / (1.0 + ageInHours);
        
        return (likes.size() * 2 + comments.size() * 3) * decayFactor;
    }
    
    void display() const;
    
    void displayWithComments() const;
};

int Post::postCounter = 0;

// ============== User ==============

class User {
private:
    string userId;
    string username;
    string name;
    set<User*> followers;
    set<User*> following;
    vector<Post*> posts;
    
public:
    User(const string& id, const string& uname, const string& n)
        : userId(id), username(uname), name(n) {}
    
    string getUserId() const { return userId; }
    string getUsername() const { return username; }
    string getName() const { return name; }
    
    void follow(User* user) {
        if (user != this) {
            following.insert(user);
            user->followers.insert(this);
        }
    }
    
    void unfollow(User* user) {
        following.erase(user);
        user->followers.erase(this);
    }
    
    bool isFollowing(User* user) const {
        return following.find(user) != following.end();
    }
    
    const set<User*>& getFollowing() const { return following; }
    const set<User*>& getFollowers() const { return followers; }
    
    void addPost(Post* post) {
        posts.push_back(post);
    }
    
    const vector<Post*>& getPosts() const { return posts; }
    
    void displayProfile() const {
        cout << "\n========== @" << username << " ==========" << endl;
        cout << "Name: " << name << endl;
        cout << "Followers: " << followers.size() << " | Following: " << following.size() << endl;
        cout << "Posts: " << posts.size() << endl;
        cout << "================================\n" << endl;
    }
};

// ============== Post Implementation ==============

Post::Post(User* a, const string& c)
    : author(a), content(c), timestamp(time(nullptr)) {
    postId = "P" + to_string(++postCounter);
    
    // Extract hashtags
    istringstream iss(content);
    string word;
    while (iss >> word) {
        if (!word.empty() && word[0] == '#') {
            hashtags.push_back(word);
        }
    }
}

void Post::display() const {
    cout << "\n┌──────────────────────────────────────┐" << endl;
    cout << "│ @" << author->getUsername() << " - " << postId << endl;
    cout << "├──────────────────────────────────────┤" << endl;
    cout << "│ " << content << endl;
    
    if (!hashtags.empty()) {
        cout << "│ ";
        for (const auto& tag : hashtags) {
            cout << tag << " ";
        }
        cout << endl;
    }
    
    cout << "├──────────────────────────────────────┤" << endl;
    cout << "│ ❤ " << likes.size() << " likes | 💬 " << comments.size() << " comments" << endl;
    
    // Display timestamp
    char timeStr[20];
    struct tm* timeinfo = localtime(&timestamp);
    strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M", timeinfo);
    cout << "│ 🕒 " << timeStr << endl;
    cout << "└──────────────────────────────────────┘" << endl;
}

void Post::displayWithComments() const {
    display();
    
    if (!comments.empty()) {
        cout << "\n💬 Comments:" << endl;
        for (const auto& comment : comments) {
            comment->display();
        }
    }
    cout << endl;
}

// ============== Comment Implementation ==============

void Comment::display() const {
    cout << "  └─ @" << author->getUsername() << ": " << text << endl;
}

// ============== Feed Generator ==============

class FeedGenerator {
public:
    static vector<Post*> generateFeed(User* user, const map<string, unique_ptr<Post>>& allPosts,
                                     int limit = 10) {
        vector<Post*> feed;
        
        // Get posts from followed users
        for (User* followedUser : user->getFollowing()) {
            for (Post* post : followedUser->getPosts()) {
                feed.push_back(post);
            }
        }
        
        // Also include own posts
        for (Post* post : user->getPosts()) {
            feed.push_back(post);
        }
        
        // Sort by timestamp (most recent first)
        sort(feed.begin(), feed.end(), [](Post* a, Post* b) {
            return a->getTimestamp() > b->getTimestamp();
        });
        
        // Limit results
        if (feed.size() > limit) {
            feed.resize(limit);
        }
        
        return feed;
    }
    
    static vector<Post*> getTrendingPosts(const map<string, unique_ptr<Post>>& allPosts,
                                         int limit = 10) {
        vector<Post*> trending;
        
        for (const auto& [id, post] : allPosts) {
            trending.push_back(post.get());
        }
        
        // Sort by engagement score
        sort(trending.begin(), trending.end(), [](Post* a, Post* b) {
            return a->getEngagementScore() > b->getEngagementScore();
        });
        
        // Limit results
        if (trending.size() > limit) {
            trending.resize(limit);
        }
        
        return trending;
    }
    
    static vector<Post*> searchByHashtag(const string& hashtag,
                                        const map<string, unique_ptr<Post>>& allPosts) {
        vector<Post*> results;
        
        for (const auto& [id, post] : allPosts) {
            const auto& tags = post->getHashtags();
            if (find(tags.begin(), tags.end(), hashtag) != tags.end()) {
                results.push_back(post.get());
            }
        }
        
        // Sort by timestamp
        sort(results.begin(), results.end(), [](Post* a, Post* b) {
            return a->getTimestamp() > b->getTimestamp();
        });
        
        return results;
    }
};

// ============== Social Media Platform ==============

class SocialMediaPlatform {
private:
    map<string, unique_ptr<User>> users;
    map<string, unique_ptr<Post>> posts;
    
public:
    User* createUser(const string& userId, const string& username, const string& name) {
        auto user = make_unique<User>(userId, username, name);
        User* userPtr = user.get();
        users[userId] = move(user);
        cout << "✓ User @" << username << " created" << endl;
        return userPtr;
    }
    
    Post* createPost(User* author, const string& content) {
        auto post = make_unique<Post>(author, content);
        Post* postPtr = post.get();
        string postId = post->getId();
        
        posts[postId] = move(post);
        author->addPost(postPtr);
        
        cout << "✓ Post created by @" << author->getUsername() << endl;
        return postPtr;
    }
    
    vector<Post*> getFeed(User* user, int limit = 10) {
        return FeedGenerator::generateFeed(user, posts, limit);
    }
    
    vector<Post*> getTrending(int limit = 10) {
        return FeedGenerator::getTrendingPosts(posts, limit);
    }
    
    vector<Post*> searchHashtag(const string& hashtag) {
        return FeedGenerator::searchByHashtag(hashtag, posts);
    }
    
    void displayFeed(User* user) {
        cout << "\n========== Feed for @" << user->getUsername() << " ==========" << endl;
        
        vector<Post*> feed = getFeed(user);
        
        if (feed.empty()) {
            cout << "No posts in feed. Follow some users!" << endl;
        } else {
            for (Post* post : feed) {
                post->display();
            }
        }
    }
    
    void displayTrending() {
        cout << "\n========== Trending Posts ==========" << endl;
        
        vector<Post*> trending = getTrending(5);
        
        for (Post* post : trending) {
            cout << "🔥 Score: " << (int)post->getEngagementScore() << endl;
            post->display();
        }
    }
};

// ============== Demo ==============

int main() {
    SocialMediaPlatform platform;
    
    cout << "========== Social Media Platform Demo ==========\n" << endl;
    
    // Create users
    cout << "=== Creating Users ===" << endl;
    User* alice = platform.createUser("U001", "alice", "Alice Johnson");
    User* bob = platform.createUser("U002", "bob", "Bob Smith");
    User* charlie = platform.createUser("U003", "charlie", "Charlie Brown");
    
    cout << endl;
    
    // Follow relationships
    cout << "=== Follow Relationships ===" << endl;
    alice->follow(bob);
    alice->follow(charlie);
    bob->follow(charlie);
    charlie->follow(alice);
    
    cout << "✓ @alice follows @bob and @charlie" << endl;
    cout << "✓ @bob follows @charlie" << endl;
    cout << "✓ @charlie follows @alice" << endl;
    
    alice->displayProfile();
    
    // Create posts
    cout << "=== Creating Posts ===" << endl;
    Post* post1 = platform.createPost(bob, "Hello world! My first post. #firstpost #excited");
    Post* post2 = platform.createPost(charlie, "Learning C++ design patterns today #cpp #learning");
    Post* post3 = platform.createPost(alice, "Beautiful sunset at the beach! #sunset #nature");
    Post* post4 = platform.createPost(bob, "Just finished a great book #reading #books");
    
    cout << endl;
    
    // Likes and comments
    cout << "=== Engagement ===" << endl;
    post1->like(alice);
    post1->like(charlie);
    post1->addComment(alice, "Welcome to the platform!");
    post1->addComment(charlie, "Great to see you here!");
    
    post2->like(alice);
    post2->like(bob);
    post2->addComment(alice, "Which patterns are you studying?");
    
    post3->like(bob);
    post3->like(charlie);
    post3->addComment(bob, "Amazing view!");
    
    cout << "✓ Users liked and commented on posts" << endl;
    
    // Display a post with comments
    cout << "\n=== Post Detail ===" << endl;
    post1->displayWithComments();
    
    // Display feed
    platform.displayFeed(alice);
    
    // Trending posts
    platform.displayTrending();
    
    // Search by hashtag
    cout << "\n=== Search: #learning ===" << endl;
    vector<Post*> results = platform.searchHashtag("#learning");
    cout << "Found " << results.size() << " posts" << endl;
    for (Post* post : results) {
        post->display();
    }
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Feed Algorithm**
- Chronological feed from followed users
- Engagement-based trending
- Time decay for relevance

### 2. **Engagement Metrics**
- Likes and comments tracking
- Weighted scoring (comments > likes)
- Real-time calculation

### 3. **Hashtag Support**
- Automatic extraction from post content
- Search and filtering
- Trending hashtags (extendable)

---

## Follow-up Questions

**Q1: How to implement feed caching?**
```cpp
class FeedCache {
    map<User*, vector<Post*>> cache;
    map<User*, time_t> cacheTime;
    
    bool isValid(User* user) {
        return (time(nullptr) - cacheTime[user]) < 300; // 5 min
    }
};
```

**Q2: How to handle retweets/shares?**
```cpp
class SharedPost : public Post {
    Post* originalPost;
    User* sharedBy;
    string additionalComment;
};
```

**Q3: How to implement notifications?**
```cpp
class Notification {
    User* recipient;
    NotificationType type; // LIKE, COMMENT, FOLLOW
    User* actor;
    Post* relatedPost;
    time_t timestamp;
};
```

---

## Compilation

```bash
g++ -std=c++17 social_media.cpp -o social
./social
```

---

**Next**: `hard/02-food-delivery.md`

