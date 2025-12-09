# Lean Construction AI - Mobile App

React Native mobile application for field data collection and real-time project monitoring.

## Features

- 📊 Real-time project dashboard
- 📝 Waste logging (8 DOWNTIME wastes)
- 📸 Site photo capture
- 🔔 Push notifications for alerts
- 📱 Offline capability
- 🔐 Secure authentication

## Setup

### Prerequisites

- Node.js 18+
- React Native CLI
- Xcode (for iOS)
- Android Studio (for Android)

### Installation

```bash
npm install
```

### iOS Setup

```bash
cd ios
pod install
cd ..
npm run ios
```

### Android Setup

```bash
npm run android
```

## Configuration

Update API endpoint in `src/services/api.js`:

```javascript
const API_BASE_URL = 'https://your-api-url.com';
```

## Project Structure

```
mobile/
├── App.js                 # Main app component
├── src/
│   ├── screens/          # Screen components
│   │   ├── LoginScreen.js
│   │   ├── DashboardScreen.js
│   │   ├── ProjectsScreen.js
│   │   ├── ProjectDetailScreen.js
│   │   ├── WasteLogScreen.js
│   │   ├── CameraScreen.js
│   │   └── ProfileScreen.js
│   └── services/         # API services
│       └── api.js
├── android/              # Android native code
├── ios/                  # iOS native code
└── package.json
```

## Available Scripts

- `npm start` - Start Metro bundler
- `npm run ios` - Run on iOS simulator
- `npm run android` - Run on Android emulator
- `npm test` - Run tests
- `npm run lint` - Run linter

## Building for Production

### iOS

```bash
cd ios
xcodebuild -workspace LeanConstructionAI.xcworkspace -scheme LeanConstructionAI -configuration Release
```

### Android

```bash
cd android
./gradlew assembleRelease
```

## Troubleshooting

### Metro bundler issues

```bash
npm start -- --reset-cache
```

### iOS build issues

```bash
cd ios
pod deintegrate
pod install
```

### Android build issues

```bash
cd android
./gradlew clean
```
