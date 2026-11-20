# Campus partner matching

Two Vue screens from a database course project let students find peers by interest and check the status of a partner request. They show how the client turns user input into a KES Plus API request and presents the response in a table.

| Screen | Request | What the user sees |
| --- | --- | --- |
| [Interest search](src/views/user-management/interest_search.vue) | `GET /user_management/searchUsersByInterest` with `p_keyword` | Matching users and an expandable list of their posted requests. |
| [Application status](src/views/demand-matching/application_show.vue) | `GET /demand_matching/queryApplicationStatus` with `p_application_id` | The application status, the request status and the remaining places. |

## Runtime

Both files are Vue single-file components. The archived application declares Vue 3.4.37, Element Plus 2.8.0 and KES Plus packages from the 3.1.7 release-candidate series. In the full project, `pnpm run dev` starts the KES Plus development command. That command belongs in the original project root, alongside `package.json` and `pnpm-lock.yaml`.

The two components here need the KES Plus layout components, request client and configured application services. The archive includes platform initialization SQL. The two application-specific API implementations and a restorable export of the business database have yet to be located. This folder is a source excerpt.

## Verification

During review, the request handlers from both files were exercised with synthetic inputs and a mock request client. Each handled an empty input, a successful response, an empty result and a rejected request. The check covered the request paths, parameter names and the resulting client state. Browser rendering, authentication and database execution remain unverified.
