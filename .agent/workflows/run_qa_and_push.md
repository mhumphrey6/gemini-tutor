---
description: Run unit tests, and if successful, commit and push changes to the remote repository.
---

1. Run the test suite to ensure all tests pass.
// turbo
2. Run `python -m pytest`

3. **CRITICAL CHECK**: Did the tests pass (exit code 0)?
   - **IF FAILED**: STOP IMMEDIATELY. Do NOT proceed to commit. You must now debug the failures and fix the code.
   - **IF PASSED**: Proceed to the next step.

4. Stage all changes.
// turbo
5. Run `git add .`

6. Commit the changes.
7. Run `git commit -m "QA: Automated commit after passing tests"`

8. Push the changes to the remote repository.
// turbo
9. Run `git push origin main`
