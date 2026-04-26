# 🚨 Emergency Card System - Direct Card Display

Your emergency medical information card, instantly generated and displayed in your dashboard!

## ✨ Key Features

### What You Get:
- **🎴 Instant Card Generation** - Save profile → Card appears immediately in dashboard
- **📱 Wallet-Style Card** - Red professional emergency card with QR code
- **📥 Downloadable** - Download your card as an image for your phone
- **👥 Emergency Contacts** - Display primary contact on card
- **🩸 Critical Info** - Name, age, blood type prominently displayed
- **🔄 Live Updates** - Any profile/contact change instantly updates the card

### What's Different:
❌ **NO QR CODE GENERATION STEP** - Card is generated directly!  
❌ **NO SCANNING REQUIRED** - See your card immediately in dashboard  
✅ **DIRECT DISPLAY** - Card appears right on the page  
✅ **ONE-CLICK DOWNLOAD** - Save card to your device instantly  

---

## 🚀 Quick Start (3 Steps!)

### Step 1: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Backend
```bash
python main.py
```
**Backend runs on:** `http://localhost:8000`

### Step 3: Start Frontend (New Terminal)
```bash
cd frontend
python -m http.server 3000
```
**Frontend runs on:** `http://localhost:3000`

---

## 📖 Complete Usage Guide

### 1️⃣ **Register Account**
- Open `http://localhost:3000`
- Click "Register here"
- Fill in: Name, Email, Phone, Password
- Click "Create Account"

### 2️⃣ **Complete Your Profile**
Go to **Profile** tab and fill in:

**Personal Information:**
- Age (example: 28)
- Gender (Male/Female/Other)
- **Blood Group** ⚠️ **REQUIRED** (A+, B+, O+, etc.)
- Height (example: 175 cm)
- Weight (example: 70 kg)
- Address

**Medical Information:**
- Allergies (comma-separated: Penicillin, Peanuts, Sulfa)
- Medical Conditions (Diabetes, Hypertension, etc.)
- Current Medications (with dosage)
- Additional Notes

Click **"Save Profile & Generate Card"**

### 3️⃣ **Add Emergency Contacts**
Go to **Contacts** tab:
- Name (example: Sita Devi)
- Relationship (Mother, Father, Spouse, etc.)
- Phone Number (+91 98765 43210)
- Email (optional)
- Priority (1 = Highest)

Click **"Add Contact"**

### 4️⃣ **View & Download Your Card**
Go to **Dashboard** tab:
- Your emergency card is displayed in red wallet style
- Shows: Name, Age, Blood Type, Primary Contact
- Has QR code for "SCAN FOR FULL DETAILS"
- Click **"Download Card"** to save as image

---

## 🎨 The Emergency Card

Your card displays:

```
┌──────────────────────────────────────────┐
│  ⚕️ EMERGENCY INFORMATION                │
│  Critical Medical Data                    │
├──────────────────────────────────────────┤
│  NAME                    ┌──────────┐    │
│  John Doe                │          │    │
│                          │  QR CODE │    │
│  AGE                     │   SCAN   │    │
│  28 years                │    FOR   │    │
│                          │   FULL   │    │
│  BLOOD TYPE              │ DETAILS  │    │
│  A+                      └──────────┘    │
│                                           │
│  EMERGENCY CONTACT                        │
│  Sita - +91 98765 43210                  │
├──────────────────────────────────────────┤
│  EMERGENCY MEDICAL CARD         ID: xxx  │
└──────────────────────────────────────────┘
```

---

## 💾 Downloading Your Card

### Method 1: Browser Download
1. Go to Dashboard
2. Scroll to "Your Emergency Card"
3. Click "Download Card" button
4. Card saves as `emergency-card.png`

### Method 2: Screenshot
- Take a screenshot of the card
- Crop and save to your phone

### Best Practices:
- ✅ Save to phone lock screen
- ✅ Print and keep in wallet
- ✅ Email to emergency contacts
- ✅ Upload to cloud storage

---

## 📂 Project Structure

```
final_card_system/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── index.html          # Main HTML file
    └── static/
        ├── css/
        │   └── style.css   # All styles including card
        └── js/
            └── app.js      # JavaScript logic
```

---

## 🔧 Technical Details

### Backend (FastAPI)
- **Framework:** FastAPI
- **Database:** SQLite (emergency_card.db)
- **Authentication:** JWT tokens
- **Password Security:** Bcrypt hashing

### Frontend
- **Framework:** Vanilla JavaScript
- **Card Rendering:** HTML/CSS generated dynamically
- **Download:** html2canvas library (loaded from CDN)
- **Styling:** Custom CSS

### Key API Endpoints

**Authentication:**
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login

**User:**
- `GET /api/user/me` - Get current user info

**Profile:**
- `GET /api/profile` - Get profile
- `POST /api/profile` - Save profile

**Contacts:**
- `GET /api/contacts` - List contacts
- `POST /api/contacts` - Add contact
- `DELETE /api/contacts/{id}` - Delete contact

**Card:**
- `GET /api/card/data` - Get card data (JSON)

**Logs:**
- `GET /api/logs` - Access logs

---

## 🎯 How It Works

### The Flow:
1. **User fills profile** → Clicks "Save Profile & Generate Card"
2. **Backend saves data** → Returns success
3. **Frontend fetches card data** → Calls `/api/card/data`
4. **JavaScript generates card HTML** → Injects into dashboard
5. **Card displays immediately** → With red wallet styling
6. **User clicks download** → html2canvas captures card
7. **Image saves to device** → `emergency-card.png`

### Card Generation Logic:
```javascript
// Frontend fetches card data
GET /api/card/data → {
  user_name: "John Doe",
  age: 28,
  blood_group: "A+",
  primary_contact: {name, phone},
  profile_id: "uuid..."
}

// JavaScript generates HTML
generateCardHTML(data) → 
  <div class="wallet-card">
    <!-- Red card with info -->
  </div>

// Display in dashboard
cardDisplay.innerHTML = cardHTML
```

---

## 🐛 Troubleshooting

### Card Not Showing?
**Problem:** Dashboard shows no card  
**Solution:**  
1. Complete your profile first
2. Make sure blood group is selected (required!)
3. Click "Save Profile & Generate Card"
4. Go to Dashboard tab

### Download Not Working?
**Problem:** Download button does nothing  
**Solution:**  
1. Check browser console (F12) for errors
2. Make sure card is visible on page
3. Try refreshing the page
4. Check browser allows downloads

### Blood Group Required Error?
**Problem:** Can't save profile  
**Solution:**  
- Blood Group field is **required**
- Select a blood type from dropdown
- Cannot be left empty

### Backend Connection Error?
**Problem:** Frontend can't connect to backend  
**Solution:**  
1. Make sure backend is running on port 8000
2. Check terminal for backend errors
3. Try: `http://localhost:8000/` in browser (should show JSON)

### Port Already in Use?
**Problem:** Can't start server  
**Solution:**  
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

---

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Session management
- ✅ Access logging
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS protection

**Note:** Change `SECRET_KEY` in production!

---

## 📱 Mobile Responsive

The card and entire system work perfectly on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Desktop browsers

Card adapts to screen size automatically.

---

## 🎨 Customization

### Change Card Color:
Edit `frontend/static/css/style.css`:
```css
.wallet-card {
    background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
    /* Change to any color! */
}
```

### Change Card Size:
```css
.wallet-card {
    max-width: 650px; /* Adjust this */
}
```

---

## 🚀 Future Enhancements

Potential features to add:
- [ ] Multiple card designs (Type 1, Type 2, Type 3)
- [ ] PDF export alongside PNG
- [ ] Email card to contacts
- [ ] Print-friendly version
- [ ] Multi-language support
- [ ] Medical history timeline
- [ ] Medication reminders
- [ ] Doctor information
- [ ] Insurance details
- [ ] Share via WhatsApp/Email directly

---

## 📝 Development Notes

### No QR Library Needed!
- QR code displayed using external API
- `https://api.qrserver.com/v1/create-qr-code/`
- No server-side QR generation
- No PIL/Pillow dependency

### Download Implementation:
- Uses `html2canvas` library
- Loads dynamically from CDN
- Captures card as canvas
- Converts to PNG blob
- Triggers browser download

---

## 💡 Tips & Best Practices

### For Users:
1. **Complete profile fully** - More info = better emergency response
2. **Add multiple contacts** - Set priorities correctly
3. **Keep card updated** - Review quarterly
4. **Save card offline** - Don't rely on internet only
5. **Share with contacts** - Let them know you have this

### For Developers:
1. **Backup database regularly** - `emergency_card.db`
2. **Change SECRET_KEY in production**
3. **Use HTTPS in production**
4. **Set up proper CORS in production**
5. **Monitor access logs**

---

## ❓ FAQ

**Q: Do I need to scan the QR code on the card?**  
A: No! The card is displayed directly in your dashboard. The QR code is just visual design.

**Q: Can I edit the card after creating it?**  
A: Yes! Just update your profile or contacts, and the card regenerates automatically.

**Q: Where is my data stored?**  
A: Locally in `emergency_card.db` SQLite file on your computer.

**Q: Can I use this offline?**  
A: Backend needs to be running, but you can download the card image for offline use.

**Q: Is my data secure?**  
A: Yes, passwords are hashed, tokens are used for auth, and data stays on your machine.

**Q: Can I have multiple cards?**  
A: One card per account, but you can create multiple accounts if needed.

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review browser console (F12) for errors
3. Check both backend and frontend are running
4. Verify all fields are filled correctly

---

## 📄 License

This project is for educational and personal use.

---

**Made with ❤️ for emergency preparedness**

🚑 **Stay Safe. Stay Prepared. Save Lives.**
