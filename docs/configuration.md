# Configuration guide

The exported workflow ships with placeholders instead of real values. After importing, search the workflow (Ctrl/Cmd + F in the n8n editor) for each placeholder below and replace it.

## 1. Credentials

| n8n credential type | Placeholder name | What to put in it |
|---|---|---|
| Telegram API | `Telegram Bot` | Bot token from @BotFather |
| Google Gemini (PaLM) API | `Gemini API` | Gemini API key |
| Header Auth | `Jira API Auth` | Name: `Authorization`, Value: `Bearer <personal access token>` |

After import, open any node that shows a credential warning and select your credential. Node IDs and webhook IDs were intentionally removed; n8n generates new ones.

## 2. Placeholders in nodes

| Placeholder | Replace with | Where |
|---|---|---|
| `https://jira.example.com` | Your Jira base URL | ~24 HTTP and Code nodes |
| `PROJ` | Your Jira project key | `Build Parent Payload`, `Build Sub Task Payloads`, agent system prompt, and example JQL |
| `board/1` | Your Agile board ID (`/rest/agile/1.0/board/<id>`) | `Fetch Active Sprint`, `Fetch Sprint Info`, `Fetch Sprints For Move` |
| `'10001'`, `'10002'`, `'10003'` | Your issue-type IDs for Task, Sub-task, Bug (`GET /rest/api/2/issuetype`) |
| `customfield_10020` | Your Sprint custom field (`GET /rest/api/2/field`, the one whose schema ends in `:gh-sprint`) | `Build Parent Payload`, `Build Sub Task Payloads` |
| Priority IDs (`'10000'`, `'1'`…`'5'`) | Your instance's priority IDs | `PRIO` map in the Code nodes that build payloads |
| `ADMIN_TELEGRAM_ID` | The admin's numeric Telegram user ID | 12 Code nodes that define `ADMIN_CHAT`, plus the `USERS` map in `Identify User` |
| `LEAD_TELEGRAM_ID`, `MEMBER_TELEGRAM_ID` | Numeric Telegram IDs of other team members | `USERS` map in `Identify User` |
| `@your_telegram_handle` | Handle shown to people who are denied access | `ADMIN_CONTACT` in `Identify User` |
| `YOUR-JOIN-CODE` | A passphrase guests can type to request access | `JOIN` in `Check Approval` |

> **Tip:** a user can learn their numeric Telegram ID by messaging the bot. Unknown users are shown their ID so they can send it to the admin.

## 3. Team members

The five sample people (`alice`, `bob`, `carol`, `dave`, `erin`) appear in several places. Replace them with your real Jira usernames **consistently**:

- `USERS` map in `Identify User` (Telegram ID → role, display name, Jira username, `JIRAUSER…` key for Tempo)
- `PEOPLE` and `PEOPLE_FA` maps in the Code nodes (tag alias → Jira username → display name)
- The agent's system prompt in `Review And Estimate` (the `@tag` → assignee mapping and the allowed-assignee lists)
- The assignee button rows in the assignee menu nodes

Roles (enforced by the `CAP` table in `Check Approval`):

| Role | Allowed actions |
|---|---|
| `admin` | Everything: create, approve, wizard, assign, change fields, move between sprints, change status, log time, attach files, reports, and replying to / approving guest requests |
| `lead` | Create, approve, wizard, assign, view, change status, log time, attach files, reports |
| `member` | Create, approve, wizard, view, change status, log time, attach files (no team-wide reports, no re-assigning, no sprint moves) |
| `guest` | Submit a task request and attach a photo. The request is forwarded to the admin and only reaches Jira after approval. Guests can also ask for access with the join code |

Every role can use the personal "my tasks" and search views.

> **Known quirk:** the comment in `Identify User` mentions a read-only `viewer` role, but `CAP` has no `viewer` entry, so an unrecognised role falls back to `member` permissions. If you want a true read-only role, add a `viewer` entry to `CAP` in the Code nodes that define it (`Check Approval`, `Pick Photo`, `Build Move Request`, `Read Button`, `Pick Transition`, …).

## 4. Labels and statuses

The agent prompt allows these labels: `Backend`, `Frontend`, `DevOps`, `BackOffice`, `Test`, `R&D`. Statuses assumed: `To Do`, `In Progress`, `Testing`, `Pending`, `Done`. Change them in the agent prompt **and** in the Code nodes that validate them if your Jira differs.

Every created issue also gets a `telegram` label so that any "new issue" alert workflow can ignore bot-created tickets.

## 5. Model

The workflow uses `models/gemini-flash-lite-latest` for both the agent and voice transcription. Swap the model node if you prefer another provider; the structured-output parser keeps the contract the same.

## 6. Smoke test after setup

1. Message the bot from the admin account: `Fix login button alignment #p3 >backlog`.
2. Confirm you get a preview card, not a created issue.
3. Approve it and check that the issue appears in Jira with the `telegram` label.
4. Send a voice note and confirm the "I heard: …" echo.
5. Message from a non-listed account and confirm it is treated as a guest (its request goes to the admin for approval).
