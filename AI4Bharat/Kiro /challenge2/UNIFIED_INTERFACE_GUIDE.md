# 🚀 Unified Automation Tool - Complete Guide

## ✅ NOW RUNNING!

**URL**: http://127.0.0.1:7863

**All-in-One Interface**: File Automation + Email Summarization

---

## 🎯 What's Included

### File Automation (3 Features)
1. **📝 Rename Files** - Batch rename 100+ files with patterns
2. **📁 Organize Files** - Auto-organize by type or date
3. **📊 Summarize Files** - Generate file statistics

### Email Automation (2 Features)
4. **🔌 Connect to Email** - Connect to Gmail/Outlook/Yahoo
5. **📧 Summarize Emails** - Get email summaries from your inbox

---

## 📝 Tab 1: Rename Files

### How to Use:
1. **Directory Path**: Enter full path (e.g., `C:\Users\YourName\Documents\Photos`)
2. **Rename Pattern**: Enter pattern with placeholders:
   - `{n}` = Sequential number (1, 2, 3...)
   - `{name}` = Original filename
   - `{ext}` = File extension
3. **Extensions**: Filter by extensions (e.g., `.jpg,.png`)
4. **Preview Mode**: ✓ Check to see changes first
5. **Click**: "Execute Rename"

### Examples:
```
Pattern: photo_{n}.jpg
Result: photo_1.jpg, photo_2.jpg, photo_3.jpg...

Pattern: 2024_{n}_{name}.{ext}
Result: 2024_1_vacation.jpg, 2024_2_beach.png...

Pattern: file_{n}.txt
Result: file_1.txt, file_2.txt, file_3.txt...
```

---

## 📁 Tab 2: Organize Files

### How to Use:
1. **Directory Path**: Enter full path (e.g., `C:\Users\YourName\Downloads`)
2. **Organization Rule**:
   - **type** = Organize by file type (images, documents, code, etc.)
   - **date** = Organize by modification date (YYYY-MM folders)
3. **Conflict Strategy**:
   - **skip** = Skip if file exists
   - **overwrite** = Replace existing file
   - **rename** = Add number suffix (file_1.txt, file_2.txt)
4. **Preview Mode**: ✓ Check to see changes first
5. **Click**: "Execute Organization"

### File Categories:
- **images/** → .jpg, .png, .gif, .bmp
- **documents/** → .pdf, .doc, .docx, .txt
- **videos/** → .mp4, .avi, .mkv, .mov
- **audio/** → .mp3, .wav, .flac
- **code/** → .py, .js, .java, .cpp
- **spreadsheets/** → .xls, .xlsx, .csv
- **archives/** → .zip, .tar, .gz, .rar
- **other/** → Everything else

---

## 📊 Tab 3: Summarize Files

### How to Use:
1. **Directory Path**: Enter full path
2. **Extensions**: Filter by extensions (e.g., `.txt,.md,.py`)
3. **Output File**: Optional - save summary to file
4. **Click**: "Generate Summary"

### What You Get:
- File name and path
- File size (human-readable)
- Line count
- Word count
- Format detection (JSON, CSV, XML)
- Modification date

---

## 🔌 Tab 4: Connect to Email

### How to Use:
1. **Email Address**: Enter your email (e.g., `yasmeen87151@gmail.com`)
2. **Password**: Enter App Password (NOT regular password!)
3. **Provider**: Select "Gmail"
4. **Click**: "Connect to Email"
5. **Wait for**: "✅ Successfully connected" message

### Get Gmail App Password:

**Step-by-Step:**
1. Go to: https://myaccount.google.com/security
2. Click **2-Step Verification** (enable if not already)
3. Scroll to **App Passwords**
4. Click **Select app** → Choose "Mail"
5. Click **Select device** → Choose "Other (Custom name)"
6. Type: "Email Summarizer"
7. Click **Generate**
8. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
9. Paste in the "Password" field above
10. Click "Connect to Email"

**Important**: 
- ✅ Use App Password (16 characters)
- ❌ Don't use regular Gmail password

---

## 📧 Tab 5: Summarize Emails

### How to Use:
1. **First**: Connect to email in Tab 4
2. **Email Folder**: Enter folder name (default: `INBOX`)
   - Click "List Available Folders" to see options
3. **Number of Emails**: Adjust slider (1-100)
4. **Unread Only**: ✓ Check for only unread emails
5. **Save to File**: ✓ Check to download summary
6. **Output Filename**: Enter filename if saving
7. **Click**: "Fetch & Summarize Emails"

### What You Get:
```
✅ Successfully analyzed 10 email(s) from INBOX

================================================================================
📧 EMAIL SUMMARY REPORT
================================================================================
Generated: 2024-12-06 15:30:45
Total Emails: 10
Total Size: 2.45 MB
Emails with Attachments: 3

📊 Top Senders:
   John Doe <john@example.com>: 3 email(s)
   Jane Smith <jane@company.com>: 2 email(s)

--------------------------------------------------------------------------------

📧 Email 1
   From: John Doe <john@example.com>
   Subject: Project Update - Q4 2024
   Date: 2024-12-06 14:25:30
   Size: 45.23 KB
   📎 Has Attachments
   Preview: Hi team, I wanted to share the latest updates...

[... more emails ...]
```

---

## 🎯 Common Use Cases

### Use Case 1: Organize Downloads Folder
1. **Tab**: Organize Files
2. **Directory**: `C:\Users\YourName\Downloads`
3. **Rule**: type
4. **Preview**: ✓
5. **Result**: Files organized into categories

### Use Case 2: Rename Vacation Photos
1. **Tab**: Rename Files
2. **Directory**: `C:\Users\YourName\Pictures\Vacation`
3. **Pattern**: `bali_trip_{n}.jpg`
4. **Extensions**: `.jpg,.jpeg`
5. **Preview**: ✓
6. **Result**: bali_trip_1.jpg, bali_trip_2.jpg...

### Use Case 3: Morning Email Triage
1. **Tab**: Connect to Email → Connect
2. **Tab**: Summarize Emails
3. **Folder**: INBOX
4. **Count**: 50
5. **Unread Only**: ✓
6. **Result**: Quick overview of overnight emails

### Use Case 4: Weekly Email Digest
1. **Tab**: Summarize Emails
2. **Folder**: INBOX
3. **Count**: 100
4. **Save to File**: ✓
5. **Filename**: `weekly_digest.txt`
6. **Result**: Downloadable weekly summary

---

## 💡 Pro Tips

### File Operations:
- ✅ **Always use Preview Mode first** - See changes before executing
- ✅ **Test with small folder first** - Verify pattern works
- ✅ **Backup important files** - Just in case
- ✅ **Use specific extensions** - Avoid processing wrong files

### Email Operations:
- ✅ **Use App Password** - Never regular Gmail password
- ✅ **Start with 10 emails** - Test connection first
- ✅ **Save important summaries** - Use "Save to File"
- ✅ **Check Unread Only** - For quick triage

---

## ⚠️ Troubleshooting

### File Operations

**"Directory not found"**
- Check path is correct
- Use full path (e.g., `C:\Users\...`)
- Check folder exists

**"No files to process"**
- Check extension filter
- Verify files exist in directory
- Try without extension filter

### Email Operations

**"Connection failed"**
- Use App Password, not regular password
- Enable 2-Step Verification first
- Check email address is correct

**"No emails found"**
- Check folder name (case-sensitive)
- Click "List Available Folders"
- Try "INBOX" (all caps)

**"Login error"**
- Generate new App Password
- Copy full 16-character password
- Remove any spaces

---

## 🌟 Interface Features

### All Tabs Include:
- ✅ Clear instructions
- ✅ Input validation
- ✅ Error messages
- ✅ Success confirmations
- ✅ Preview/dry-run modes
- ✅ Download capabilities

### User-Friendly:
- 🎨 Clean, modern interface
- 📱 Responsive design
- 🔒 Secure password fields
- 💾 File download options
- 📊 Real-time results
- ℹ️ Built-in help

---

## 🆚 Why Unified Interface?

### Before (Separate Tools):
```
❌ Open file automation tool
❌ Close it
❌ Open email tool
❌ Switch between windows
❌ Remember different commands
```

### Now (Unified Interface):
```
✅ One interface for everything
✅ Switch between tabs
✅ All features in one place
✅ Consistent UI
✅ Easy to use
```

---

## 📊 Quick Reference

| Feature | Tab | Key Input | Output |
|---------|-----|-----------|--------|
| Rename Files | Tab 1 | Directory + Pattern | Renamed files |
| Organize Files | Tab 2 | Directory + Rule | Organized folders |
| Summarize Files | Tab 3 | Directory | File statistics |
| Connect Email | Tab 4 | Email + Password | Connection status |
| Summarize Emails | Tab 5 | Folder + Count | Email summaries |

---

## 🎉 You're All Set!

### Quick Start:
1. **Open**: http://127.0.0.1:7863
2. **Choose**: File automation OR Email summarization
3. **Follow**: Instructions in each tab
4. **Enjoy**: Automated boring tasks!

### For File Automation:
- Use Tabs 1-3 (Rename, Organize, Summarize Files)
- Always enable Preview Mode first
- Enter full directory paths

### For Email Summarization:
- Use Tabs 4-5 (Connect, Summarize Emails)
- Get Gmail App Password first
- Connect before summarizing

---

**Stop wasting time on boring tasks!** 🚀✨

*The Unified Automation Tool combines everything you need in one beautiful interface.*

**Currently Running**: http://127.0.0.1:7863
