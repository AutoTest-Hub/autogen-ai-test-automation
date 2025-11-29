# Quick Start Guide - AI Test Automation Platform

## 🚀 Get Started in 5 Minutes

### Prerequisites Check
- ✅ PostgreSQL running on localhost:5432
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed

### 1. Start the Backend (Terminal 1)
```bash
cd /home/ubuntu/autogen-ai-test-automation
python3 api/main_postgres_full.py
```
**Expected Output**: `🚀 Enterprise API Server ready with full 21-table schema!`

### 2. Start the Frontend (Terminal 2)
```bash
cd /home/ubuntu/autogen-ai-test-automation/web-dashboard
npm run dev
```
**Expected Output**: `Local: http://localhost:5173/`

### 3. Access the Application
- **URL**: http://localhost:5173
- **Username**: tester@demo.com
- **Password**: demo123

### 4. Create Your First Test

1. **Login** with the demo credentials
2. **Navigate** to Create Tests page
3. **Select Application**: Choose "E-commerce Demo" from dropdown
4. **Enter Details**:
   - Test Name: "My First Test Suite"
   - Description: "Testing the platform functionality"
   - Priority: High
5. **Click "Create Tests"** and watch the real-time progress!

### 5. Test Requirements.json Upload

1. **Upload the sample file**: `/home/ubuntu/autogen-ai-test-automation/sample_requirements.json`
2. **Watch** as it auto-populates the form
3. **Create tests** based on the requirements

## ✅ Verification Checklist

- [ ] Backend API health check: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend loads without errors
- [ ] Login works with demo credentials
- [ ] Applications dropdown populates (31 apps)
- [ ] Test creation starts successfully
- [ ] Real-time progress updates work
- [ ] Test completion shows results
- [ ] Duplicate detection triggers on repeat names
- [ ] Requirements.json upload and validation works

## 🔧 Quick Troubleshooting

### Backend Won't Start
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check if port 8000 is available
netstat -tlnp | grep 8000
```

### Frontend Won't Start
```bash
# Clear npm cache and reinstall
cd web-dashboard
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database Issues
```bash
# Reset database if needed
sudo -u postgres psql -d test_automation_platform -f database/complete_platform_setup.sql
```

### Authentication Problems
- Clear browser localStorage
- Check console for token errors
- Verify backend is running on port 8000

## 📋 Sample Test Data

### Applications Available
- E-commerce Demo Store (OpenCart)
- Banking Demo Portal (TestFire)
- HRMS Demo Platform (OrangeHRM)
- Healthcare Management System
- And 27 more...

### Test Templates
- **E-commerce**: Product catalog, shopping cart, checkout
- **Banking**: Account management, transactions, security
- **HRMS**: Employee management, leave, payroll
- **Healthcare**: Patient management, appointments, billing

## 🎯 Key Features to Test

1. **Template Selection**: Try different application types
2. **Real-time Progress**: Watch the 4 agent phases
3. **Duplicate Detection**: Create tests with same names
4. **Requirements Upload**: Use the sample JSON file
5. **Error Handling**: Try invalid inputs
6. **Success Flow**: Complete end-to-end test creation

## 📞 Need Help?

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Console Logs**: Check browser developer tools
- **Backend Logs**: Check terminal running the API server

---

**Ready to go!** 🎉 The platform is fully functional and ready for testing.
