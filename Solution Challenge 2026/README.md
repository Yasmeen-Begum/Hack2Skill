# CrisisSync 🛡️

**CrisisSync** is a high-performance, real-time crisis management and emergency coordination platform designed specifically for hospitality venues (hotels, resorts, and convention centers). It bridges the critical gap between distressed guests, on-site personnel, and first responders through AI-driven analysis and multi-channel synchronization.

---

## 🚀 Key Features

- **Command Center Dashboard**: EOC-style real-time situational awareness with KPI monitoring.
- **AI Crisis Assistant**: Powered by **Gemma 4** (via HuggingFace) for response planning and template generation.
- **Interactive Floor Maps**: Visual tracking of incidents and personnel across multiple floors.
- **Multi-Channel Alerting**: Automated and manual broadcasts to **WhatsApp, Gmail, and Slack** via n8n.
- **Personnel Tracker**: Real-time deployment and status management of security and medical teams.
- **SOS Portal**: A high-priority interface for guests and staff to report emergencies instantly.

---

## 🛠️ Technology Stack

- **Frontend**: Flutter (Windows, Web, Android, iOS)
- **State Management**: Provider
- **Backend**: Firebase (Firestore, Auth, Cloud Messaging)
- **AI Engine**: Gemma 4 (HuggingFace Inference API)
- **Integration Layer**: n8n (Automation Workflow)
- **Protocol**: Model Context Protocol (MCP) for AI tool access

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1.  **Flutter SDK**: [Install Flutter](https://docs.flutter.dev/get-started/install) (v3.3.0 or higher)
2.  **Node.js**: [Install Node.js](https://nodejs.org/) (for the MCP server)
3.  **Visual Studio 2022**: With "Desktop development with C++" workload (for Windows builds)
4.  **n8n Instance**: Cloud or self-hosted for external messaging.

---

## ⚙️ Setup & Installation

### 1. Clone & Fetch Dependencies
```bash
# Navigate to the project directory
cd CrisisSync

# Install Flutter dependencies
flutter pub get
```

### 2. Enable Platform Support
If the `windows` or `web` folders are missing, run:
```bash
flutter create . --platforms windows,web,android
```

### 3. Configure AI (HuggingFace)
1. Open `lib/core/services/gemma_service.dart`.
2. Replace `_hfToken` with your actual HuggingFace API Token.

### 4. Configure Integrations (n8n)
1. Open `lib/core/services/n8n_service.dart`.
2. Update `_webhookUrl` with your n8n Webhook URL.
3. In n8n, create a workflow that routes this webhook to **WhatsApp** and **Gmail**.

---

## 🏃 Running the Application

### Launch on Windows (Recommended)
```bash
flutter run -d windows
```

### Launch on Web (Chrome)
```bash
flutter run -d chrome
```

### Build for Production
```bash
# Windows
flutter build windows

# Android
flutter build apk
```

---

## 🤖 AI MCP Server (Optional)

We have included a **Model Context Protocol (MCP)** bridge to allow external AI agents to interact with CrisisSync tools.

1. Navigate to the server folder: `cd mcp-server`
2. Install dependencies: `npm install`
3. Start the server: `npm start`

---

## 📁 Project Structure

- `lib/core/`: Centralized logic (Models, Providers, Services, Theme).
- `lib/features/`: UI modules for each feature (Dashboard, SOS, Map, etc.).
- `lib/shared/`: Reusable widgets like GlassCards and StatusBadges.
- `assets/`: UI assets and configuration files.

---

## 🔐 Security & Safety
CrisisSync is designed for mission-critical response. While the AI provides guidance, it includes deterministic fallbacks for high-priority incidents (Fire/Medical) to ensure life-safety protocols are never dependent solely on a cloud API.

---

## 📄 License
Internal Development - CrisisSync Hospitality Platform.
