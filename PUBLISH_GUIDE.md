# Publish to your GitHub account (Rokib1605)

The connected GitHub tool cannot create new repositories, so follow these one-time steps:

1. Visit https://github.com/new while logged in as Rokib1605.
2. Repository name: `campusprint-backend-demo`. Visibility: **Public**.
3. Do **not** tick Create README, .gitignore, or license (these files are already included).
4. Click **Create repository**.
5. Open a terminal inside the extracted `campusprint-backend-demo` folder.
6. Run:

```bash
git init
git add .
git commit -m "CampusPrint backend CRUD and integration tests"
git branch -M main
git remote add origin https://github.com/Rokib1605/campusprint-backend-demo.git
git push -u origin main
```

Then open https://github.com/Rokib1605/campusprint-backend-demo and select Actions to see the test workflow.

If Git asks for login, use GitHub web/browser authorization or a personal access token. Never put credentials in the source code.
