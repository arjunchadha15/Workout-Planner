# UserPreferences Integration Note

## ⚠️ Important: UserPreferences Class

The code references `UserPreferences.shared` to persist user data. If this class doesn't exist in your app yet, you'll need to add a `goal` property to it.

## Option 1: If UserPreferences Already Exists

Add this property to your existing `UserPreferences` class:

```swift
class UserPreferences: ObservableObject {
    static let shared = UserPreferences()
    
    // Existing properties...
    @Published var username: String = ""
    @Published var gender: OnboardingData.Gender?
    @Published var bodyweight: String = ""
    @Published var experienceLevel: OnboardingData.ExperienceLevel?
    
    // ADD THIS:
    @Published var goal: OnboardingData.Goal? {
        didSet {
            // Optionally persist to UserDefaults
            if let goal = goal {
                UserDefaults.standard.set(goal.rawValue, forKey: "userGoal")
            }
        }
    }
    
    init() {
        // Load goal from UserDefaults
        if let goalString = UserDefaults.standard.string(forKey: "userGoal"),
           let goal = OnboardingData.Goal(rawValue: goalString) {
            self.goal = goal
        }
    }
}
```

## Option 2: If UserPreferences Doesn't Exist

Create a new file `UserPreferences.swift`:

```swift
import Foundation
import Combine

class UserPreferences: ObservableObject {
    static let shared = UserPreferences()
    
    @Published var username: String = "" {
        didSet {
            UserDefaults.standard.set(username, forKey: "username")
        }
    }
    
    @Published var gender: OnboardingData.Gender? {
        didSet {
            if let gender = gender {
                UserDefaults.standard.set(gender.rawValue, forKey: "gender")
            }
        }
    }
    
    @Published var bodyweight: String = "" {
        didSet {
            UserDefaults.standard.set(bodyweight, forKey: "bodyweight")
        }
    }
    
    @Published var experienceLevel: OnboardingData.ExperienceLevel? {
        didSet {
            if let level = experienceLevel {
                UserDefaults.standard.set(level.rawValue, forKey: "experienceLevel")
            }
        }
    }
    
    @Published var goal: OnboardingData.Goal? {
        didSet {
            if let goal = goal {
                UserDefaults.standard.set(goal.rawValue, forKey: "goal")
            }
        }
    }
    
    @Published var userId: String? {
        didSet {
            if let userId = userId {
                UserDefaults.standard.set(userId, forKey: "userId")
            }
        }
    }
    
    private init() {
        // Load from UserDefaults
        username = UserDefaults.standard.string(forKey: "username") ?? ""
        bodyweight = UserDefaults.standard.string(forKey: "bodyweight") ?? ""
        
        if let genderString = UserDefaults.standard.string(forKey: "gender") {
            gender = OnboardingData.Gender(rawValue: genderString)
        }
        
        if let levelString = UserDefaults.standard.string(forKey: "experienceLevel") {
            experienceLevel = OnboardingData.ExperienceLevel(rawValue: levelString)
        }
        
        if let goalString = UserDefaults.standard.string(forKey: "goal") {
            goal = OnboardingData.Goal(rawValue: goalString)
        }
        
        userId = UserDefaults.standard.string(forKey: "userId")
    }
    
    func clearAll() {
        username = ""
        gender = nil
        bodyweight = ""
        experienceLevel = nil
        goal = nil
        userId = nil
        
        UserDefaults.standard.removeObject(forKey: "username")
        UserDefaults.standard.removeObject(forKey: "gender")
        UserDefaults.standard.removeObject(forKey: "bodyweight")
        UserDefaults.standard.removeObject(forKey: "experienceLevel")
        UserDefaults.standard.removeObject(forKey: "goal")
        UserDefaults.standard.removeObject(forKey: "userId")
    }
}
```

## Option 3: Simple Alternative Without UserPreferences

If you don't want to create UserPreferences, modify the onboarding completion in `NewOnboardingView.swift`:

Change:
```swift
let preferences = UserPreferences.shared
preferences.username = onboardingData.username
preferences.gender = onboardingData.gender
preferences.bodyweight = onboardingData.bodyWeight
preferences.experienceLevel = onboardingData.experienceLevel
preferences.goal = onboardingData.goal
```

To:
```swift
// Save directly to UserDefaults
UserDefaults.standard.set(onboardingData.username, forKey: "username")
UserDefaults.standard.set(onboardingData.gender?.rawValue, forKey: "gender")
UserDefaults.standard.set(onboardingData.bodyWeight, forKey: "bodyweight")
UserDefaults.standard.set(onboardingData.experienceLevel?.rawValue, forKey: "experienceLevel")
UserDefaults.standard.set(onboardingData.goal?.rawValue, forKey: "goal")
```

## Verification

After implementing, verify that the goal is saved by adding this in your app:

```swift
if let savedGoal = UserDefaults.standard.string(forKey: "goal") {
    print("✅ User's goal is saved: \(savedGoal)")
}
```

Or with UserPreferences:
```swift
if let goal = UserPreferences.shared.goal {
    print("✅ User's goal is: \(goal.rawValue)")
}
```

---

**Choose the option that best fits your existing architecture!**
