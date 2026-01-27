# 📧 Gmail SMTP Setup Guide for LegalConnect

## ⚠️ Current Issue

You're seeing **"Failed to send verification email"** because Gmail SMTP credentials are not configured in the `.env` file.

---

## ✅ Step-by-Step Fix

### Step 1: Enable 2-Step Verification on Gmail

1. Go to https://myaccount.google.com/security
2. Scroll to "Signing in to Google"
3. Click **"2-Step Verification"**
4. Follow the prompts to enable it (if not already enabled)

### Step 2: Generate Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. You may need to sign in again
3. In the "Select app" dropdown, choose **"Mail"**
4. In the "Select device" dropdown, choose **"Other (Custom name)"**
5. Type **"LegalConnect"** as the name
6. Click **"Generate"**
7. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)
   - ⚠️ You won't be able to see this password again!

### Step 3: Update `.env` File

1. Open the file: `d:\Project Law\legal-connect\backend\.env`

2. Find these lines (around lines 8-10):
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password-here
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

3. Replace with YOUR credentials:
   ```env
   MAIL_USERNAME=karthikdon2006@gmail.com
   MAIL_PASSWORD=abcd efgh ijkl mnop
   MAIL_DEFAULT_SENDER=karthikdon2006@gmail.com
   ```
   
   **Important Notes**:
   - Use the **16-character App Password**, NOT your regular Gmail password
   - The App Password may have spaces - that's OK, keep them
   - Use the same email for both `MAIL_USERNAME` and `MAIL_DEFAULT_SENDER`

### Step 4: Restart Backend Server

The backend needs to reload the `.env` file:

1. Go to the terminal running the backend
2. Press **Ctrl+C** to stop it
3. Run this command to restart:
   ```powershell
   cd backend
   ..\\.venv\\Scripts\\python.exe app.py
   ```

4. You should see the server start without errors

### Step 5: Test Email Sending

1. Go to http://localhost:3001
2. Try to login with `karthikdon2006@gmail.com`
3. Click **"Resend Verification Email"**
4. Check the backend terminal - you should see:
   ```
   [EMAIL] Attempting to send verification email to karthikdon2006@gmail.com
   [EMAIL] ✅ Successfully sent verification email to karthikdon2006@gmail.com
   ```
5. Check your Gmail inbox for the verification email

---

## 🔍 Troubleshooting

### Error: "Authentication Failed"

**Cause**: Wrong App Password or 2-Step Verification not enabled

**Solution**:
1. Verify 2-Step Verification is ON
2. Generate a NEW App Password
3. Copy it exactly (with spaces)
4. Update `.env` file
5. Restart backend

### Error: "Connection timed out"

**Cause**: Firewall or network issue

**Solution**:
1. Check your internet connection
2. Temporarily disable firewall
3. Make sure port 587 is not blocked

### Error: "MAIL_USERNAME not configured"

**Cause**: `.env` file not updated or backend not restarted

**Solution**:
1. Double-check `.env` file has real credentials
2. Restart backend server
3. Check for typos in `.env`

### Still Not Working?

Check the backend terminal for detailed error messages. The improved error logging will show:
- Exact error type
- Specific cause
- Suggested solutions

---

## 📝 Example `.env` Configuration

Here's what your complete `.env` file should look like:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

# Email Configuration (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=karthikdon2006@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
MAIL_DEFAULT_SENDER=karthikdon2006@gmail.com
FRONTEND_URL=http://localhost:3001
```

Replace `abcd efgh ijkl mnop` with your actual 16-character App Password.

---

## ✅ After Setup

Once configured correctly:
1. ✅ Registration will send verification emails
2. ✅ "Resend Verification Email" will work
3. ✅ Forgot Password will send reset emails
4. ✅ Users can only login after verifying email

---

## 🎯 Quick Checklist

- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated
- [ ] `.env` file updated with real credentials
- [ ] Backend server restarted
- [ ] Test "Resend Verification Email" button
- [ ] Check Gmail inbox for verification email
- [ ] Click verification link
- [ ] Login successfully

---

**Need Help?** Check the backend terminal for detailed error messages with specific solutions!
