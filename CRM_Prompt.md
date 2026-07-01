You are an expert in 3CX PhoneSystem CRM integration. Your task is to create a valid XML template file (.xml) for integrating 3CX with a CRM system.

## MANDATORY PRE-GENERATION STEPS — complete these BEFORE writing any XML

**Step 1 — Resolve workspace-specific activity type IDs (REQUIRED when journaling is enabled)**

If either `ReportCall` or `ReportChat` is selected in the feature list, you MUST obtain the correct activity type IDs before generating the XML. These IDs are workspace-specific and cannot be reliably determined from documentation alone. Producing XML with guessed, placeholder, or documentation-example IDs is NOT acceptable.

Procedure:
1. If you do not already have the user's API credentials (token + email), stop immediately and ask for them. State exactly what is needed and why. Do NOT proceed to generate any XML until credentials are provided.
2. Once credentials are available, make an appropriate live REST request to the CRM's activity-types endpoint (e.g. `GET /activity_types` with the appropriate auth headers).
3. From the response, identify:
   - The ID of the activity type matching "Phone Call" (or equivalent) → used in `ReportCall`
   - The ID of the activity type matching the chat/SMS type specified in the checklist → used in `ReportChat`
4. Hard-code both resolved IDs as the `Default` values in their respective `<Parameter>` elements.
5. Document the resolved IDs in the XML header comment.

**This step is non-negotiable. Do not skip it, do not substitute a fallback, and do not generate the XML before it is complete.**

**Exception — CRM has no activity type concept:** Some CRMs use a generic Notes or Comments API for all journaling (e.g. a `POST /notes` endpoint that takes a parent record reference and a text body, with no type classification). If live API exploration (Step 2) confirms that the journaling endpoint accepts no type parameter and the CRM has no activity-types endpoint, document this explicitly in the XML header comment and skip the ID lookup. This must be confirmed via live API inspection — do NOT assume it from documentation alone. "No activity type IDs" is a valid finding, not a skipped step.

**Step 2 — Research the CRM API**

Research the CRM API independently (endpoints, field names, auth headers, match behaviour, etc.) as described in the sections below. Do not ask the user for any of this information. For anything not explicitly provided, make reasonable, well-documented assumptions.

## Required Features
Please include the following scenarios (check all that apply):
- [X] Contact lookup by phone number (mandatory — scenario with empty Id)
- [X] Contact lookup by Email (Id starts with "LookupByEmail")
> **Shared rule for LookupByEmail and all SearchContacts sub-scenarios:** omit the scenario if the CRM has no dedicated filter for that field type; use `AllowEmpty="false"` on Outputs. Per-item notes list only additional guards.
- [X] Search contacts by free text (Id starts with "SearchContacts") by the following methods:
  - [X] Search contacts by First Name (Id = "SearchContacts_FirstName")
    - "dedicated filter" means the CRM API has a field that searches on first name **specifically and independently** — a full-name field that happens to match first-name fragments does NOT qualify
  - [X] Search contacts by Last Name (Id = "SearchContacts_LastName")
    - same rule: a full-name field does NOT qualify as a dedicated last-name filter
  - [X] Search contacts by Full Name (Id = "SearchContacts_FullName")
  - [X] Search contacts by Company (Id = "SearchContacts_Company")
    - note: company search may use a **separate endpoint** (e.g. `/companies/search`) rather than the people search endpoint — research this carefully before concluding the feature is unavailable
  - [X] Search contacts by PhoneNumbers (Id = "SearchContacts_PhoneNumbers")
    - Additional guard: do NOT create if the CRM's phone number search returns an error (not just empty results) on non-digit input. Research whether the CRM strips or normalises non-numeric characters before searching. **Important:** "non-numeric characters are stripped" in API docs typically means formatting characters in otherwise numeric strings (e.g. "+1 (408) 555-1234" → "14085551234") — a purely alphabetic input (e.g. "abc") strips to empty and many CRMs reject this with a 422. **You MUST verify this with a live test using a purely alphabetic search term (e.g. "abc") before including this scenario.** Since credentials are required for the activity-type lookup, use them here too. Do not rely on documentation alone.
  - [X] Search contacts by Email (Id = "SearchContacts_Email")
- [X] Call journaling / ReportCall (Id = "ReportCall") — Activity type name: [e.g., Phone Call]
- [X] Chat journaling / ReportChat (Id = "ReportChat") — Activity type name: [REQUIRED: fill in the exact name, e.g. SMS, Note, or Chat — do not leave as placeholder]
- [X] Create contact from 3CX client (Id = "CreateContactRecordFromClient")
- [X] CFD Lookup Contacts by Number (Id = "LookupFromCFD_Contacts_LookupNumber")
- [X] CFD Lookup Contacts by ID (Id = "LookupFromCFD_Contacts_LookupID")
- [X] CFD Lookup Contacts by Free Text (Id = "LookupFromCFD_Contacts_LookupFreeQuery")
> **Shared rule for all LookupFromCFD_ scenarios:** omit the scenario if the CRM has no dedicated API filter for that search type.


## Request Target CRM Information from the User
- CRM Name:
- CRM API Base URL:
- CRM Contact Base URL:
- CRM Example Contact URL:

Once all four fields above are provided, research the CRM's API documentation independently. **Research depth:** Do not rely only on the main API reference (e.g. field types and request/response examples). Also search for how the CRM handles formatting and rendering in notes/activities (e.g. search for "[CRM name] markdown", "[CRM name] GFM", "[CRM name] CommonMark", "[CRM name] rich text", "[CRM name] HTML"). Check the CRM's developer community, best-practices docs, and integration/automation guides (e.g. Zapier, Make) where formatting or rendering is often documented. Use this deeper research to make better decisions (e.g. for recording link format and other body-content formatting).

**Research computed and sanitized field variants:** Many CRMs expose derived or computed versions of core fields alongside the raw stored value — for example a pre-sanitized phone field that already strips formatting characters, a normalized email field, or a computed display name. Always search for these before mapping the raw field. Search for "[CRM name] sanitized phone field", "[CRM name] normalized phone", "[CRM name] computed fields", and browse the contact model's full field list in the API reference rather than only the fields mentioned in examples. If a sanitized or pre-normalized variant exists, prefer it over the raw field so that no client-side transformation is needed. Document which variant you chose and why.

## If the Call journaling feature is selected:
- add a ReportCallEnabled parameter to allow the user to enable or disable the Call journaling feature, as follows:
  - <Parameter Name="ReportCallEnabled" Type="Boolean" Parent="" Editor="String" Title="Enable Call Journaling" Validation="" Default="False" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- add a child parameter "Subject", as follows: 
  - <Parameter Name="Subject" Type="String" Parent="ReportCallEnabled" Editor="String" Title="Subject:" Validation="" Default="3CX Phone System Call" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- add a child parameter "InboundCallText", as follows:
  - <Parameter Name="InboundCallText" Type="String" Parent="ReportCallEnabled" Editor="String" Title="Answered Inbound Call:" Validation="" Default="[DateTime]: Answered incoming call from [Number] [Name] to [Agent] ([Duration])[LineBreak]Transcription: [Transcription][LineBreak]Summary: [Summary][LineBreak]Sentiment: [Sentiment][LineBreak]Recording: [RecordingHyperLink]" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- add a child parameter "MissedCallText", as follows:
  - <Parameter Name="MissedCallText" Type="String" Parent="ReportCallEnabled" Editor="String" Title="Missed Call:" Validation="" Default="[DateTime]: Missed call from [Number] [Name] to [Agent]" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- add a child parameter "OutboundCallText", as follows:
  - <Parameter Name="OutboundCallText" Type="String" Parent="ReportCallEnabled" Editor="String" Title="Answered Outbound Call:" Validation="" Default="[DateTime]: Answered outgoing call from [Agent] to [Number] [Name] ([Duration])[LineBreak]Transcription: [Transcription][LineBreak]Summary: [Summary][LineBreak]Sentiment: [Sentiment][LineBreak]Recording: [RecordingHyperLink]" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- add a child parameter "NotAnsweredOutboundCallText", as follows:
  - <Parameter Name="NotAnsweredOutboundCallText" Type="String" Parent="ReportCallEnabled" Editor="String" Title="Unanswered Outbound Call:" Validation="" Default="[DateTime]: Unanswered outgoing call from [Agent] to [Number] [Name]" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- **Line breaks in parameter defaults:** Choose based on the CRM's journaling body field type, determined during API research (Step 2):
  - **Plain text or Markdown field:** use `[LineBreak]`. Do not use `&lt;br/&gt;`, `&#xA;`, `&amp;#xA;`, or literal newlines in `Default` attributes.
  - **HTML field** (field type is explicitly `html` in the CRM schema, confirmed during research): use `&lt;br/&gt;` instead of `[LineBreak]`. Raw newlines are invisible in HTML rendering — only `<br/>` produces a visible line break in the CRM UI. In the XML `Default` attribute write `&lt;br/&gt;` — the XML parser converts this to the literal text `<br/>`, which 3CX stores and expands correctly at runtime. (PostValues handles all JSON escaping automatically, so there are no JSON-safety concerns with either choice; the difference is purely visual in the CRM.)
- **Recording link format:** Using the deep-research approach described above, determine how the CRM renders activity/note body content. Use exactly one of the following in the "Recording:" line of InboundCallText and OutboundCallText:
  - **Full HTML link** — if the CRM accepts and renders HTML in the activity/note body: use `Recording: [RecordingHyperLink]`.
  - **Markdown-style link** — if the CRM accepts Markdown or CommonMark or GFM (e.g. [text](url)): use e.g. `Recording: {{Download}}([RecordingUrl])` (or equivalent link text; [RecordingUrl] is the URL variable).
  - **Plain URL only** — only if you find no evidence that the CRM accepts HTML or Markdown/CommonMark/GFM after this deeper research: use `Recording: [RecordingUrl]`.
> **Note on Markdown link syntax in 3CX:** `[Download]` must be written as `{{Download}}` in the Default attribute (since `[` and `]` are 3CX expression delimiters and must be escaped as `{{` / `}}`). The full Markdown recording value is therefore: `Recording: {{Download}}([RecordingUrl])`
- **ReportCall MUST be implemented as a single scenario using `<PostValues>` with `RequestEncoding="Json"`.** Do NOT use a `Message` attribute with nested `IIf()` or `replaceq()` — the 3CX expression parser cannot handle complex nested expressions in a `Message` string, and PostValues produces cleaner, automatically-escaped JSON in all cases.
  - **JSON-RPC envelope CRMs** (any CRM using the JSON-RPC 2.0 protocol, where every request body must contain a top-level `args` array) are NOT a reason to fall back to `Message`. Use a nested `<Array Key="args">` element inside `<PostValues>` — `<PostValues>` fully supports `<Array>`, `<Object>`, and `<Value>` children to arbitrary depth, and generates the complete JSON-RPC envelope automatically.
- **Do NOT use an activity-creation API for ReportCall.** CRM "activity create" APIs (e.g. any endpoint that creates a scheduled task, todo, or future activity record) always produce a PLANNED/FUTURE item — they cannot log a completed historical call. For call journaling, use a method that posts directly to the contact's interaction history (e.g. a message-post, chatter, or note endpoint). Research the correct historical-log API during Step 2 and confirm it creates a completed record, not a scheduled one.
- Use the known-working two-condition `SkipIf`: `SkipIf="[ReportCallEnabled]!=True||[EntityId]==&quot;&quot;"`. No call-type condition in `SkipIf` is needed.
- Use the `If` attribute on individual `<Value Key="body">` (or equivalent body-field key) elements to select the correct call-type text. The 3CX call type values are `Inbound`, `Missed`, `Outbound`, `Notanswered` (note: `Notanswered`, not `NotAnsweredOutbound`). Include one `<Value>` element per call type, each with the matching `If` condition.
- Use `Passes="2"` on body and subject `<Value>` elements with double-bracket content (e.g. `[[InboundCallText]]`): pass 1 expands the parameter value; pass 2 resolves the runtime variables inside it (`[DateTime]`, `[Number]`, etc.).
- Use `Passes="1"` for direct variable references (e.g. `[DbName]`, `[EntityId]`). Use `Passes="0"` for static literals.

## If the Chat journaling feature is selected:
- add a ReportChatEnabled parameter to allow the user to enable or disable the Chat journaling feature, and child parameter for ChatSubject, as follows:
  - <Parameter Name="ReportChatEnabled" Type="Boolean" Parent="" Editor="String" Title="Enable Chat Journaling" Validation="" Default="False" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
  - <Parameter Name="ChatSubject" Type="String" Parent="ReportChatEnabled" Editor="String" Title="Chat Subject:" Validation="" Default="3CX PhoneSystem Chat Session" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- ensure the SkipIf condition in the ReportChat scenario evaluates this Parameter
- ensure that the [ChatSubject] variable is included at the beginning of the ReportChat scenario message
- **The correct 3CX predefined variable for the chat transcript is `[ChatMessages]`** (confirmed from the official 3CX CRM Template XML Description documentation). Do NOT use `[ChatLog]`, `[ChatBody]`, or any other name — only `[ChatMessages]` exists as a predefined variable for the report chat scenario.
- **ReportCall and ReportChat typically use different CRM API endpoints or methods — research each independently.** Do not assume they share the same call pattern. A CRM may use one method for scheduling a call activity (ReportCall) and a completely different method/model for posting a chat note (ReportChat). For example, one CRM might use an activity-creation method for calls and a chatter/message-post method for chat (posting directly to the contact's message log rather than creating a scheduled activity).
- **Positional record-ID args pattern:** some CRM chat-log methods take a list of record IDs as their first positional argument (ORM-style, where the method acts on a set of records). In that case wrap `[EntityId]` in a doubly-nested array: `<Array Key=""><Array Key=""><Value Key="" Passes="1" Type="Integer">[EntityId]</Value></Array></Array>`. This produces `[[EntityId]]` in JSON — a list containing one list of one ID, matching the method signature.
- **Body separator:** use `&#x0A;` as element text content (not `&lt;br/&gt;`) to separate the chat subject from the transcript when the CRM's chat body field accepts plain text or normalises newlines. `&#x0A;` is an XML character reference for the literal newline (LF) character; it is preserved in element text content and PostValues JSON-encodes it as `\n`. Do NOT use `&#x0A;` in XML *attribute* values — the XML spec normalises it to a space there.

## If the Create contact from 3CX client feature is enabled:
- **3CX input variables for this scenario:** use `[FirstName]`, `[LastName]`, `[Email]`, and `[Number]` (the dialled/entered phone number). Do NOT use output variables such as `[PhoneMobile]` or `[PhoneBusiness]` — those are only populated from lookup results, not from the 3CX client create-contact form.
- add a CreateContactEnabled parameter to allow the user to enable or disable the Create contact from 3CX client feature, as follows:
  - <Parameter Name="CreateContactEnabled" Type="Boolean" Parent="General Configuration" Editor="String" Title="Allow contact creation directly to your CRM using 3CX Web Client" Validation="" Default="False" ListValues="" RequestUrl="" RequestUrlParameters="" ResponseScenario="" />
- **Name field format — research carefully:** CRMs differ in how they accept a contact name on creation. Research the CRM's create-contact endpoint before building the payload:
  - If the CRM accepts a **single full-name string** (e.g. `"name": "John Doe"`): concatenate [FirstName] and [LastName] into one field, e.g. `^^[FirstName] [LastName]^^`.
  - If the CRM accepts **separate first and last name fields** (e.g. `"first_name": "John", "last_name": "Doe"`): send them as individual fields.
  - Document which format the CRM requires in the scenario comment.
- **Implementation — verify first, then decide:**
  1. Inspect the CRM's create endpoint response during live testing. Check whether it returns the full contact record (name, email, phone numbers, contact URL) or only a minimal response (new record ID, or ID plus a few fields).
  2. **If the create endpoint returns only an ID or a minimal response** (most CRMs): use a two-scenario chain:
     - `CreateContactRecordFromClient` — calls the create endpoint, maps the new record's ID to `[ContactId]` via `<Variables>`, and declares `<Outputs Next="CreateContactRecordFromClient_Fetch" AllowEmpty="false">` to hand off.
     - `CreateContactRecordFromClient_Fetch` — calls the CRM's single-record fetch/read endpoint using the inherited `[ContactId]`, and populates all standard outputs (same field mapping as the phone lookup scenario).
  3. **If the create endpoint returns the full record:** a chain is unnecessary. Populate all standard outputs directly in `CreateContactRecordFromClient` from the create response.
  - Do NOT fall back to sourcing display fields (name, email, phone) from 3CX input variables in the Outputs — always read the data back from the CRM so the displayed record reflects what was actually saved.

**Activity type IDs for ReportChat:** match the activity type name specified in the checklist. If no name is specified, identify the most semantically appropriate native type for chat/SMS logging — do NOT fall back to a generic type (e.g. Note with ID 0) unless the CRM genuinely has no dedicated chat/messaging type.

## Reference Documentation
Use the following documents to assist you:
- https://www.3cx.com/docs/crm-template-xml-description/
- https://www.3cx.com/docs/crm-integration/

## CRM API Details (Research These — Do Not Ask the User)
- Field mapping to research: Contact ID, First name, Last name, Email, Company name, Contact URL pattern, and all phone number fields — see the full phone-type mapping requirement below.
- **Phone type mapping (mandatory — map ALL types):** The 3CX contact object exposes seven distinct phone output fields. For every integration you MUST research all phone number type labels the CRM uses and map each to the most semantically appropriate 3CX field. An unmapped phone type causes 3CX to discard a found contact as "no match" because its post-lookup number-validation step checks whether the searched number appears in any mapped output field — if the number is stored under an unmapped type it will never match, even though the API search returned the correct contact. The seven 3CX phone output types and their typical CRM equivalents are:
  - `PhoneBusiness`  — primary work/office number (e.g. CRM type "Work", "Business", "Office")
  - `PhoneBusiness2` — secondary business line (e.g. CRM type "Direct", "Direct Dial", "Work 2")
  - `PhoneHome`      — home number (e.g. CRM type "Home", "Personal")
  - `PhoneMobile`    — primary mobile (e.g. CRM type "Mobile", "Cell")
  - `PhoneMobile2`   — secondary mobile (e.g. CRM type "Mobile 2", "Personal Mobile") — omit only if the CRM has no second mobile type
  - `PhoneOther`     — a native "Other" phone category (e.g. CRM type "Other") — see rules below
  - `FaxBusiness`    — fax number (e.g. CRM type "Fax", "Fax Business")
  Research the CRM's phone number type vocabulary (API docs, contact model, any enum/type list). Map every type the CRM supports to one of the seven fields above. **`PhoneOther` must only be included when the CRM has a native phone type category that corresponds to "Other" (e.g. a literal "Other" entry in the CRM's type enum).** Do NOT add `PhoneOther` as a generic catch-all using `Type="Any"` for a CRM that assigns explicit types to all its phone entries — such a CRM has no untyped phones, so the catch-all would either match phones already captured by a typed variable or simply never match anything. Emit a `<Variable>` and `<Output>` pair for every type the CRM actually supports. **Never leave a phone type that the CRM uses unmapped.**

  **Exception — CRM has a typeless phone array:** Some CRMs store all phone numbers in a single array with no type or category field (every entry is just a phone-number object with no label, e.g. `[{"phone_number": "+1..."}, {"phone_number": "+2..."}]`). In this case only the first array element can be reliably extracted (see the array filter rules in the Variables section). Map the first element to `PhoneBusiness` only. All other 3CX phone output types (PhoneBusiness2, PhoneHome, PhoneMobile, PhoneMobile2, PhoneOther, FaxBusiness) must be omitted — there is no type vocabulary to map them to, and confirmed live testing shows that 3CX's Variable path resolution does not support positional array indexing (`array[0].field`, `array.0.field`, etc. — all return empty). Document this clearly in the XML header comment and note that contacts whose primary calling number is not the first in the array will not match — advise users to reorder numbers in the CRM so the most-called number is first.
- For each phone field: check whether the CRM also exposes a sanitized/normalized variant (e.g. a field containing only digits and `+`, with all spaces, dashes, and brackets already removed). If such a variant exists, prefer it over the raw field, and note the field name chosen.
- **Phone field strategy — search vs. output:**
  - **Search filters (phone lookup and SearchContacts_PhoneNumbers):** Use an OR domain to match on BOTH the sanitized variant AND the raw phone field. Some contacts may have a raw phone value but no sanitized value (e.g. when the CRM cannot normalize the number to E.164). Searching only the sanitized field will miss these contacts. Where the CRM API supports a prefix OR operator in domain filters (e.g. a `|` prefix operator), use it to combine both fields. In PostValues the OR domain is expressed as a nested `<Array>` structure: a wrapper `<Array Key="">` containing one `<Array Key="">` whose first element is the `|` string followed by two condition `<Array>` children.
  - **Output values:** Prefer the sanitized variant when it is valid; fall back to the raw field when the sanitized field is absent, empty, or the sentinel "false" value. See the expression guidance below for the correct comparison string.

## Authentication Details
The `<Authentication>` element supports exactly three Type values:

If `Type="No"` (custom header-based auth — API keys, multi-header schemes, etc.):
- All credential headers are added manually via `<Headers><Value Key="HeaderName">value</Value></Headers>` inside each `<Request>`.
- Parameter names in 3CX console: [e.g., ApiKey, ApiUserEmail]
- Header name(s): [e.g., X-API-Key, X-PW-AccessToken]

If `Type="Basic"` (HTTP Basic Auth or Bearer token):
- Username parameter name: [e.g., ApiUser]
- Password / token parameter name: [e.g., ApiKey]
- 3CX injects the `Authorization` header automatically.

If `Type="Scenario"` (token-exchange or credential-lookup flows):
- Use when the CRM requires a pre-flight API call to obtain a session token or resolve a numeric user ID before other requests can be made (e.g. trading credentials for a session token or user ID, OAuth 2.0 token exchange).
- The `<Authentication>` element contains only a `<Value>` child naming the auth scenario Id. The auth scenario lives **inside `<Scenarios>`** alongside all other scenarios:
  ```xml
  <Authentication Type="Scenario">
    <Value>Auth</Value>
  </Authentication>
  ```
- **Do NOT** nest the `<Scenario>` directly inside `<Authentication>` — this causes `System.ArgumentNullException` at runtime.
- The auth scenario is a `<Scenario Id="Auth" Type="REST" EntityId="" EntityOrder="">` with the following confirmed-working structure:
  - `RequestContentType=""` (leave empty — not `application/json`)
  - `<Rules>` anchoring on the token/id field: `<Rule Type="Any" Ethalon="">result</Rule>`
  - `<Variables>` mapping the response value to a named variable, with an empty `<Filter />` child:
    ```xml
    <Variables>
      <Variable Name="Uid" LookupValue="" Path="result"><Filter /></Variable>
    </Variables>
    ```
  - **`<Outputs>` — this is mandatory and is what publishes the variable to all subsequent scenarios.** Without it the variable is local to the auth scenario and resolves to empty in all other scenarios. Use `HeaderName` / `HeaderValue` / `BearerExpiration` output types:
    ```xml
    <Outputs AllowEmpty="false">
      <Output Type="HeaderName"       Passes="0" Value="X-Auth-Uid" />
      <Output Type="HeaderValue"      Passes="0" Value="[Uid]" />
      <Output Type="BearerExpiration" Passes="0" Value="1" />
    </Outputs>
    ```
    The `HeaderName` / `HeaderValue` pair is the mechanism by which 3CX publishes `[Uid]` as a globally available variable in all subsequent scenarios. 3CX also injects it as a custom HTTP header into every outgoing request; the CRM will ignore it if it does not use it, so the header name can be any arbitrary value. `BearerExpiration` controls how often 3CX re-runs the auth scenario (in minutes); set to a value appropriate for the CRM's token/key lifetime.
- 3CX calls the auth scenario automatically on startup and whenever the token expires. The resolved variable (e.g. `[Uid]`) is then available in every subsequent scenario — embed it in JSON request bodies as needed.
- **`Passes="0"` is sufficient for parameter references** (`[DbName]`, `[UserEmail]`, `[ApiKey]`, etc.) inside the auth scenario's `<PostValues>` — parameters are resolved regardless of pass level in the auth scenario context.

## Phone Number Formatting
- Prefix handling: **Determine via live test** — do NOT ask the user. Once you have API credentials and at least one contact with a known stored phone number (obtained during the contact lookup or activity-type research), run the following four test queries against the CRM's phone search endpoint, substituting the stored number in each format:
  1. **Plus** — prepend `+` (E.164 style, e.g. `+18137689202`)
  2. **Off** — digits only, no prefix (e.g. `18137689202`)
  3. **AsIs** — local/national digits, no country code (e.g. `8137689202`)
  4. **Zeros** — replace `+` with `00` (e.g. `0018137689202`)
  For each test, issue the CRM's phone-search call with that formatted value and record which return results and which do not. Then apply this decision logic:
  - If only one format matches → use that format.
  - If multiple formats match (common when the CRM uses `$contains` / substring matching) → prefer **Plus**, because it sends the canonical E.164 string the CRM normalises to, minimising false-positive overlap.
  - If **Zeros** is the only match → use Zeros.
  - If no format matches → investigate why before proceeding (the stored number may be in an unexpected format).
  Document the test results and your chosen setting in the XML header comment.
- MaxLength: always set to `[MaxLength]` — this is a built-in 3CX variable that carries the digit-strip length configured in the 3CX PBX itself. Do NOT ask the user for a value; do NOT hardcode a number. The `<Number>` element must always read `MaxLength="[MaxLength]"`.
- **MaxLength and `[Number]` in PostValues — critical:** When 3CX sends a POST request via `<PostValues>`, the `[Number]` variable is substituted as the raw digit-stripped value produced by MaxLength **without** the Prefix being applied. For example, with MaxLength=6 and an incoming number "+18137689201", `[Number]` becomes `"689201"` (last 6 digits, no `+`). This means:
  - If the CRM stores phone numbers in full E.164 format (i.e., the Prefix test showed "Plus" as the only match), an **exact** filter for `"689201"` will never match the stored value `"+18137689201"`, regardless of the Prefix setting in `<Number>`.
  - **Required additional live test:** After the Prefix test, search the CRM's phone endpoint using only the last 6 digits of a known stored number (no prefix, no country code) and record whether the CRM returns the correct contact. Perform this test with both exact match and with any `$contains` / suffix / substring operator the CRM supports.
  - **Decision rule — CRM stores full E.164 (Prefix="Plus"):** If the CRM stores numbers in E.164 and supports a `$contains`, suffix, or substring operator on the phone field, use that operator (not exact match) for the base phone lookup (empty Id) and `LookupFromCFD_Contacts_LookupNumber`. Exact match is only safe when MaxLength is guaranteed to cover the full international number length, which is never a safe assumption. Document this decision in the XML header comment.
  - **Decision rule — CRM stores local/national format (Prefix="Off" or "AsIs"):** Exact match is safe because the stripped `[Number]` value will match the locally-stored number format directly.

## Additional Requirements
- Template version: always set to `1`. Do NOT ask the user for a value.
- Country: always set to `Global` — the attribute is mandatory on the `<Crm>` element but is not used by 3CX at runtime. Do NOT ask the user for a value.
- Max concurrent requests: **Determine via API research** — do NOT ask the user. Research the CRM's API documentation for any stated concurrent-request limit, rate-limit, or connection-pool ceiling. Then apply this logic:
  1. If the API documentation states a maximum concurrent-request (or per-second/per-minute request) limit → set `MaxConcurrentRequests` to **50% of that value**, rounded down to the nearest integer, with a minimum of 1.
  2. If no such limit is documented → use a default of **2**.
  In all cases the value must be a positive integer (≥ 1). Document the source and calculation in the XML header comment.
- Supports emojis: **Determine via API research** — do NOT ask the user. Research whether the CRM's API and its note/activity/comment body fields accept and correctly store Unicode emoji characters (e.g. search for "[CRM name] emoji support", "[CRM name] unicode", "[CRM name] UTF-8 notes"). Apply this logic:
  - If research confirms emojis are supported (UTF-8 / Unicode text fields, no known stripping) → set `SupportsEmojis="true"`.
  - If research reveals emojis are stripped, replaced, or cause errors → set `SupportsEmojis="false"`.
  - If research is inconclusive → set `SupportsEmojis="false"` (conservative default).
  Document the finding and source in the XML header comment.

---

## Instructions for the AI

Using the information above, generate a complete and valid 3CX CRM Integration XML file following these rules:

1. Root element must be <Crm> with attributes: Name, Version, Country, SupportsEmojis.
2. Include a <Number> element with appropriate Prefix and MaxLength.
3. Include a <Connection> element with MaxConcurrentRequests.
4. Include a <Parameters> element with all user-configurable settings (URL, credentials, WorkspaceID, etc.) as <Parameter> children. Each <Parameter> must contain the following attributes:
  - Parent — set according to the parameter's role:
    - Standard connection/credential parameters (URL, API key, workspace ID, etc.): `Parent="General Configuration"`
    - Feature enable/disable Boolean parameters that have child parameters of their own (e.g. ReportCallEnabled, ReportChatEnabled): `Parent=""` — only use empty Parent when the parameter itself has children
    - Feature Boolean parameters with no child parameters (e.g. CreateContactEnabled): `Parent="General Configuration"`
    - Child parameters that belong to a feature (e.g. Subject, InboundCallText): `Parent="[FeatureToggleParameterName]"` (e.g. `Parent="ReportCallEnabled"`)
  - Type - can be one of String, Password, Boolean, Integer, Double, DateTime, OAuth
  - Editor - can be one of String, Sql
  - Title - a Description label for the field
  - **Comments must not contain workspace-specific or customer-specific identifiers.** XML comments (including the file header) must describe the CRM product in general, not the specific instance used during research. Do not include workspace URLs, subdomain names, database names, user IDs, API keys, live-test dates, or any other value that identifies the customer whose credentials were used. Field notes in comments must be written as facts about the CRM product (e.g. "this CRM stores numbers with formatting characters") not about the research instance (e.g. "this instance has no mobile field").
  - **Default values must not contain workspace-specific or customer-specific identifiers.** Before setting a Default, research the CRM's URL structure to determine which portions of the provided example URLs or credentials are workspace-specific (e.g. subdomain, database name, organisation ID, tenant ID, account slug). Any parameter whose value would differ between two different customers of the same CRM (URL base, workspace name, API key, etc.) must have an empty Default (`Default=""`). Only pre-fill a Default when the value is the same for every deployment of that CRM (e.g. a fixed, shared API endpoint such as `https://api.somecrm.com` that contains no per-customer identifier). If a URL parameter contains both a fixed path segment and a workspace-specific subdomain or path, the entire Default must be left empty.
  - **Prefer human-readable credential identifiers.** When the CRM API accepts either a human-readable identifier (email address, username, login name) or an opaque numeric/internal ID for authentication, always expose the human-readable form as the user-facing parameter. Numeric internal user IDs (e.g. an internal UID or owner ID that must be resolved from an email address or username) are hard for users to locate and easy to get wrong. If the API ultimately requires the numeric ID, use `Type="Scenario"` authentication to resolve it automatically from the human-readable credential — the user should never have to look up or enter an internal ID manually.
  - **Do not conflate parameters that happen to share the same value in the research instance.** Two parameters having the same value during research does not mean they represent the same concept or will always match in production. Research each parameter's meaning independently. For example, some CRMs use a per-customer subdomain in the URL while also requiring a separate database or workspace name in API call bodies — these may coincide in a standard SaaS deployment but are distinct concepts that can differ in self-hosted or custom-configured instances. Define each parameter independently with its own Title and empty Default, and never describe one as "the same as" or "derived from" the other in parameter titles or documentation.
5. Include an <Authentication> element. The Type attribute must be one of exactly three values:
  - `Type="No"` — custom / header-based authentication (no built-in mechanism; inject all credential headers manually via `<Headers><Value Key="...">` inside each `<Request>`). Use this for API-key-in-custom-header schemes (e.g. `X-PW-AccessToken`) or any auth that does not fit the two types below.
  - `Type="Basic"` — HTTP Basic Auth or Bearer token. 3CX adds the `Authorization` header automatically using the configured username/password or token.
  - `Type="Scenario"` — use when the CRM requires a pre-flight API call to resolve credentials (e.g. trading an email + API key for a numeric user ID, or an OAuth token exchange). The `<Authentication>` element contains only `<Value>ScenarioId</Value>`. The auth scenario lives inside `<Scenarios>` and MUST include `<Rules>`, `<Variables>`, and `<Outputs>` with `HeaderName` / `HeaderValue` / `BearerExpiration` — the `<Outputs>` block is what publishes the resolved value as a globally available variable. See the Authentication Details section for the complete confirmed-working structure.
6. Include a <Scenarios> element containing all required scenario children.
7. For each <Scenario>:
   - Include a "Type" attribute which can have one of these values: "REST", "SQLDatabase", or "NoSQLDatabase".
   - Set the correct Id (empty for phone lookup, "ReportCall" for journaling, etc.)
   - Include a <Request> element with correct Url, RequestContentType, RequestEncoding, RequestType, and ResponseType. For a POST with a JSON body: `<Request SkipIf="" Url="[CrmApiUrl]/contacts/search" MessagePasses="0" Message="" RequestContentType="" RequestEncoding="Json" RequestType="Post" ResponseType="Json">` (body is supplied via `<PostValues>` — never via the Message attribute). For a GET: `<Request SkipIf="" Url="[CrmApiUrl]/contacts/[ContactId]" MessagePasses="0" Message="" RequestContentType="" RequestEncoding="UrlEncoded" RequestType="Get" ResponseType="Json">`.
     - **3CX search variable name:** the variable that holds the user's search input is always `[SearchText]` — never `[SearchCriteria]` or any other name.
     - **Page size:** Use page_size of 20 for all scenarios (phone lookup, email lookup, and all SearchContacts variants), as long as the CRM API supports it. Do not use a higher or lower value unless the CRM imposes a different limit.
     - **Match behaviour — always prefer the CRM default:** CRM search endpoints often support multiple match modes (e.g. exact, partial/suffix, fuzzy/permuted). The preferred approach is to rely on the CRM's default partial or fuzzy matching wherever it is available — a small risk of false positives is acceptable in exchange for a higher match rate. Research the default match behaviour for each field (phone, name, company, email):
       - If the CRM **defaults to partial or fuzzy** for a field, use a plain value and do NOT add an explicit match parameter.
       - If the CRM **defaults to exact** matching for a field where partial results are desirable, add the CRM-specific parameter to request partial or fuzzy matching.
       - Document the default behaviour in the scenario comment (e.g. "This CRM defaults to partial/fuzzy; plain value used to maximise match rate").
     - **Live verification (preferred when credentials are available):** If the user's API credentials have already been collected (e.g. for the activity-type lookup), make a test search call with a known partial phone number fragment *without* any explicit match parameter to verify the actual default behaviour before deciding whether to add one. State the result and your decision in a comment.
     - **Building JSON payloads — always use PostValues**: For ALL POST requests, use **RequestEncoding="Json"** with **RequestContentType=""**, **Message=""**, and a **&lt;PostValues&gt;** child. Never build JSON inside the Message attribute. PostValues supports three child element types:
       - **&lt;Value Key="name" If="" SkipIf="" Passes="0" Type="String|Integer|Boolean|..."&gt;** — a JSON leaf property or array element. `Type` controls JSON serialisation: `String` → quoted string, `Integer` → number, `Boolean` → `true`/`false`. `If` conditionally includes the element; `SkipIf` conditionally excludes it.
         - When `<Value>` is a **child of an `<Object>`**: set `Key` to the property name — e.g. `Key="limit"` produces `"limit": 20`.
         - When `<Value>` is a **child of an `<Array>`**: set `Key=""` (empty). The value becomes an unnamed array element — e.g. `<Value Key="" Type="String">phone</Value>` inside an `<Array>` produces the string `"phone"` as the next element of the JSON array. **Never use a non-empty Key inside an Array — JSON arrays have no property names.**
       - **&lt;Object Key="name" If="" SkipIf=""&gt;** — a JSON object `{}`. Children are `<Value>`, `<Object>`, or `<Array>` elements. Use `Key=""` when the object is itself a child of an `<Array>` (array element, no property name).
       - **&lt;Array Key="name" If="" SkipIf=""&gt;** — a JSON array `[]`. All direct children MUST use `Key=""` regardless of their type (`<Value>`, `<Object>`, or `<Array>`), because array elements are positional, not named. Nest `<Array Key="">` within `<Array>` to produce nested arrays. Use `Key=""` when the array is itself a child of an outer `<Array>`.
       - **Domain nesting for execute_kw-style CRMs:** `execute_kw` splats its `method_args` array as positional arguments, removing one level of nesting before the domain reaches the search method. To compensate, the domain must be wrapped one extra time in `PostValues`. For **any** number of conditions, the structure in `PostValues` must be **three levels deep**: (1) the `method_args` outer array, (2) the domain list (a single `<Array Key="">`), (3) the leaf condition tuples (`<Array Key="">` children). A single-condition domain `[["field","op","val"]]` therefore requires three nested `<Array>` elements — **not two** — so that after the execute_kw splatting the domain received by the search method is `[["field","op","val"]]` rather than the flat (invalid) `["field","op","val"]`. An OR domain like `["|",cond1,cond2]` also uses three levels: the outer args-array → the domain array (containing `"|"` + two sub-arrays) → the leaf tuple arrays. The 2-condition implicit-AND domain `[[cond1,cond2]]` likewise uses three levels: outer array → domain array containing two leaf sub-arrays. In all cases, leaf condition arrays (`["field","op","val"]`) sit at the **third** nesting level inside `<PostValues>`.
       - Self-closing `<Object Key="" If="" SkipIf=""/>` produces an empty object `{}`. This is the correct way to pass an empty kwargs dict.
       - **JSON-RPC envelope CRMs** require a top-level `args` array: use `<Array Key="args">` inside `<PostValues>` with nested `<Array>` children for domain tuples, kwargs objects, and create-vals arrays. PostValues handles all JSON serialisation and escaping automatically — no `^^`, `{{}}`, or `replaceq()` hacks are needed.
       - For **ReportCall**, use four separate `<Value Key="note">` (or equivalent body-field key) elements, each with `If="[CallType]==Inbound"`, `If="[CallType]==Missed"`, `If="[CallType]==Outbound"`, and `If="[CallType]==Notanswered"`, to select the correct call-type text without any `IIf()` expressions. **Important:** the `If` attribute on PostValues `<Value>` elements uses unquoted identifiers — do NOT add `&quot;` around the value. This is distinct from `SkipIf` on `<Request>` elements, which requires `&quot;`-quoted string literals to avoid `System.InvalidCastException`.
     - **MessagePasses**: use `0` for simple messages (single variable substitution). Use `2` when the Message string contains parameter references that themselves contain runtime variables (e.g. a parameter whose value includes `[DateTime]` or `[Number]`) so that both levels are resolved. Not applicable when using PostValues.
     - SkipIf is evaluated as a full boolean expression — comparison operators (==, !=) and logical operators (||, &&) are supported directly. For example: SkipIf="[ReportCallEnabled]!=True||[EntityId]==&quot;&quot;" skips when journaling is disabled OR no contact was matched.
     - Use IIf() only when the expression would not otherwise resolve to a plain true/false literal on its own (e.g. a ternary default value). Bare comparisons and || / && chains do NOT require IIf() wrapping.
     - Use SkipIf="" only when the scenario should never be skipped.
     - Custom headers will be inside a <Headers> sub-element of the <Request>.
     - Each custom header will be a <Value> sub-element of <Headers> with a "Key" attribute.
   - Include <Rules> to validate whether the response contains a result
     - The `<Rules>` section only determines whether a result was found — it does **NOT** set a root context for Variable path resolution. Variable `Path` attributes are always **absolute from the JSON response root**, regardless of what the Rule content says.
     - Use `<Rule Type="Any" Ethalon="">path.to.field</Rule>` where the path points to a field that is non-empty when at least one record was found. For a response like `{"result": [{"id": 10, ...}]}`, use `<Rule Type="Any" Ethalon="">result.id</Rule>` — this correctly fails on an empty results array `{"result": []}`. Do NOT use `<Rule Type="Any" Ethalon="">result</Rule>` for search_read responses: an empty array may still pass that check.
     - Exception: for non-array responses where `result` is a scalar value (e.g. an authentication endpoint returning a session token or user ID, or a create endpoint returning the new record's ID), use `<Rule Type="Any" Ethalon="">result</Rule>` since the value is directly at the `result` key.
   - Include <Variables> to map response fields to named variables
     - Every <Variable> must include a correct "Path" attribute — absolute from the JSON response root.
     - **For JSON-RPC CRMs:** all data is nested under a `result` key. Variable paths must include this prefix: `Path="result.id"`, `Path="result.name"`, etc. Setting `Path="id"` will instead match the JSON-RPC envelope's own `"id"` field (always `1`), not the contact's ID. This is the single most common source of empty or wrong variable values for JSON-RPC integrations.
     - **Filter syntax:** to filter an array field (e.g. phone_numbers, emails), place a `<Filter>` element as a **direct child** of `<Variable>` — do NOT wrap it in a `<Filters>` parent. Example: `<Variable Name="Email" Path="emails.email"><Filter><Rule Type="Equals" Ethalon="work">emails.category</Rule></Filter></Variable>`. Using `<Filters><Filter>` will cause 3CX to ignore the filter silently.
     - **Array field extraction — critical rules confirmed via live test:**
       - **An empty `<Filter />` only works for single-element arrays.** Confirmed via live test: for any array that may contain more than one element, `<Filter />` with no Rule child returns empty — the variable is NOT populated. Never use `<Filter />` on an array that could have multiple entries.
       - **Arrays WITH category labels** (e.g. `emails.category = "work"`, `phone_numbers.type = "mobile"`): use `Type="Equals"` with the exact Ethalon matching the CRM's category label. Example where the array is at the response root: `<Rule Type="Equals" Ethalon="work">emails.category</Rule>`. Example where the array is nested under a wrapper key: `<Rule Type="Equals" Ethalon="Work">parties.phoneNumbers.type</Rule>`.
       - **Arrays WITHOUT category labels** (typeless arrays — e.g. a phone_numbers array where entries have no type field): use `Type="Any" Ethalon=""` on any non-null sub-field within the array element. Example where the array is at the response root: `<Rule Type="Any" Ethalon="">phone_numbers.phone_number</Rule>`. Example where the array is nested: `<Rule Type="Any" Ethalon="">parties.phoneNumbers.number</Rule>`. This selects the first element where that sub-field is non-empty. Note that only ONE element can be selected this way — there is no mechanism to extract elements by position (see the phone type mapping section).
       - **Filter Rule paths are absolute from the JSON response root** — exactly the same as Variable `Path` attributes. For a response `{"parties": [{"phoneNumbers": [{"type": "Work", "number": "..."}]}]}` the correct Filter Rule path is `parties.phoneNumbers.type` (full root path including the wrapper key), NOT `phoneNumbers.type` (relative to the array element). 3CX's own documentation examples appear to use short paths only because those examples place the array directly at the response root, making the array name the full path. For any response where data is nested under a wrapper key (e.g. `parties`, `result`, `data`), that wrapper key must be included in both the Variable `Path` and the Filter Rule path.
   - Include <Outputs> with the correct output types (ContactUrl is mandatory; at least one of FirstName/LastName/CompanyName; at least one phone field for lookup)
     - Set `AllowEmpty` on the `<Outputs>` element according to the scenario's checklist constraint: use `AllowEmpty="false"` for any scenario marked "do NOT allow empty outputs" (LookupByEmail and all SearchContacts variants); use `AllowEmpty="true"` for the base phone lookup scenario (which must always return a result even if only partial data is available). Explicitly include EntityId, EntityType, ContactUrl, PhoneMobile and PhoneBusiness outputs in all contact-returning scenarios, to ensure the 3CX client correctly caches and displays the record.
     - **EntityType value must be capitalised**: use `Value="Person"` and `Value="Company"` — not lowercase.
     - **`<Output Value="...">` expressions must be wrapped in `[...]`.** A bare function call such as `Value="IIf(...)"` is treated as a literal string by 3CX and is NOT evaluated. Always write `Value="[IIf(...)]"` (or `Value="[[Variable].Method()]"` etc.) so that 3CX recognises the content as an expression to evaluate.
     - Define the ContactUrl using a combination of a base URL parameter and the dynamic [ContactId], ensuring the internal CRM routing fragment (e.g., fullProfile=people-) is included.
     - **String literals in SkipIf comparisons MUST be quoted with `&quot;`...`&quot;`.** The 3CX `||` operator requires both operands to be actual booleans. Comparisons involving boolean parameters (`[BoolParam]!=True`) return booleans and are safe. Comparisons involving string variables return a boolean ONLY when the right-hand side is a properly quoted string literal (e.g. `[CallType]!=&quot;Inbound&quot;`) or an empty-string literal (`[EntityId]==&quot;&quot;`). An **unquoted** non-boolean identifier (e.g. `[CallType]!=Inbound`) is treated as a variable reference, resolves to null, and the comparison returns a String — causing `System.InvalidCastException: Unable to cast object of type 'System.String' to type 'System.Boolean'` at runtime. Always write string value comparisons as `[Variable]==&quot;Value&quot;` or `[Variable]!=&quot;Value&quot;`.
8. Use 3CX expression syntax for dynamic values: [VariableName], IIf(), .Replace(), .ToString() etc.
   - Simple substitution: [VariableName]
   - Method calls on a variable MUST use double-bracket form: [[VariableName].Method()] — the inner brackets resolve the variable, the outer brackets delimit the expression. Using [VariableName.Method()] will throw "Unknown function: VariableName.Method".
   - \n and \r in Replace() arguments are treated as literal two-character strings and do NOT match actual LF/CR bytes at runtime.
   - XML character references (&#xA; / &#xD;) ARE resolved to real control characters by the XML parser, but a bare control character in an unquoted Replace() argument crashes 3CX's expression parser with "Stack empty".
   - **Line breaks inside `<PostValues> <Value>` element content:** use `&#x0A;` (XML LF character reference). The XML parser delivers a real newline character to the PostValues JSON serialiser, which encodes it correctly as `\n` in the JSON string. Do NOT use `[LineBreak]` inside `<Value>` content — it is only resolved in parameter `Default` attribute values, not in PostValues element content.
   - **JSON boolean values become .NET Pascal-case strings:** 3CX is a .NET application. When a CRM API returns a JSON boolean `false` or `true`, 3CX stores the mapped variable as the .NET string `"False"` or `"True"` (capital first letter) — NOT as the lowercase JSON literals `"false"` / `"true"` and NOT as a native boolean. Any string comparison against these values must use the Pascal-case form. For example, to detect a missing/invalid sanitized phone field: `[IIf([PhoneSanitized]==&quot;&quot;||[PhoneSanitized]==&quot;False&quot;,[PhoneRaw],[PhoneSanitized])]`. Using `==&quot;false&quot;` (lowercase) or `==false` (boolean literal) will silently fail to match.
9. Escape special characters in expressions: [ → {{, ] → }}, " → ^^
   - This applies to ALL square brackets in the Message string, including JSON array literals. For example, a JSON array value must be written as `{{^^[Variable]^^}}` not `[^^[Variable]^^]`, otherwise 3CX will misinterpret the outer brackets as an expression delimiter.
   - To produce a JSON **array of objects** in a Message string, use `{{ { } }}` (with spaces): the outer `{{` and `}}` escape to `[` and `]`, and the inner literal `{` and `}` wrap the object. The spaces prevent triple-brace parsing ambiguity. For example, `{{ {^^email^^: ^^value^^} }}` produces `[{"email": "value"}]`.
10. Scenario output rules — apply per scenario type:
    - **ReportCall / ReportChat**: do NOT include `<Rules>`, `<Variables>`, or `<Outputs>` — only a `<Request>` element (write-only, response is ignored).
    - **CreateContactRecordFromClient**: after inspecting the create endpoint's live response, implement as either (a) a **two-scenario chain** (if the create endpoint returns only an ID or a minimal response) — first scenario maps new record ID to `[ContactId]` and uses `<Outputs Next="CreateContactRecordFromClient_Fetch" AllowEmpty="false">`, second scenario fetches the full record; or (b) a **single scenario** (if the create endpoint returns the full record) — populate all standard outputs directly from the create response. See the feature section and the chaining section for the decision criteria.
    - **CFD lookup scenarios** (Id starts with "LookupFromCFD_"): include only `<Rules>` (to anchor the response record) and a `<Request>` element — do NOT include `<Variables>` or `<Outputs>`. CFD scenarios pass data directly to the Call Flow Designer flow; no variable mapping or contact display population is needed.
11. **Chained scenarios** — when one API call is not enough to complete a task:
    - Any scenario can hand off to a chained scenario by setting the `Next` attribute on its `<Outputs>` element: `<Outputs Next="TargetScenarioId" AllowEmpty="true|false">`. The target scenario Id must match an existing `<Scenario Id="...">` in the file.
    - The chained scenario is executed **once for each result that passes the Rules filter** of the parent scenario.
    - The chained scenario **inherits every variable** set in the parent (and grandparent) scenarios — no re-fetching or re-passing is needed.
    - The chain terminates when either: (a) the final scenario in the chain is reached and outputs are set, or (b) a scenario's request returns an empty response (or no records pass the filter) and its `<Outputs>` has `AllowEmpty="false"`.
    - **Only the last scenario in the chain** populates the outputs that 3CX uses for display and matching — intermediate scenarios' `<Outputs>` elements serve only to declare `Next=` and `AllowEmpty=`.
    - **When to use chaining:**
      - **Only chain when a live test demonstrates that the second request exposes data not present in the first response.** Before adding a chain, compare the first API call's full response against what a subsequent single-record fetch returns. If both responses contain the same fields and values, the chain adds a wasted API call and must not be used. Many CRM search/query endpoints return the full contact record including all nested arrays — verify this before assuming a fetch is needed.
      - Any other scenario where the first call returns only a reference (ID, URL) that must be resolved by a second call — and this is confirmed via live test comparison, not assumed.
    - **Naming convention:** append a descriptive suffix to the parent scenario's Id: `CreateContactRecordFromClient` → `CreateContactRecordFromClient_Fetch`. Use `_Fetch`, `_Read`, `_Resolve`, or similar.
    - Chained (child) scenarios follow the same rules as standalone scenarios: they must include a `<Request>`, and should include `<Rules>`, `<Variables>`, and `<Outputs>` when they produce contact data.
12. Add XML comments explaining each major section.

## XML Validity Constraints — MUST follow or 3CX will reject the file with "incorrect file format"

- **No `--` inside comment bodies.** The XML spec forbids the sequence `--` anywhere between `<!--` and `-->`. This applies everywhere inside a comment: separator lines, prose sentences (e.g. "field X -- note Y"), arrows written as `-->` embedded in comment text, and any other use. Always use `=` signs for separators (`<!-- ======= -->`) and rephrase prose to avoid `--` (e.g. use "==" or ": " instead). Before emitting the file, scan every comment body for `--` and replace.

## Pre-output Self-check

Before emitting the file, mentally scan for:
0. **Activity type IDs resolved?** If `ReportCall` or `ReportChat` is included, confirm that both IDs were obtained via a live API call in this session — not guessed, not copied from documentation examples. If not, STOP and request credentials before continuing.
1. Any comment containing `--` → replace hyphens with `=` signs.
2. Every contact-returning scenario has a `<Output Type="ContactUrl" .../>`.
3. Every `SkipIf` that gates on an enabled flag uses the `[Flag]!=True||[EntityId]==&quot;&quot;` pattern. Every string-value comparison in a `SkipIf` expression uses `&quot;`-quoted literals (e.g. `[CallType]!=&quot;Inbound&quot;`) — no bare unquoted identifiers appear on the right-hand side of a string comparison.
4. **ReportCall uses PostValues — no exceptions:** no `Message` attribute, no `MessagePasses`, no `replaceq()`, no chained scenarios; `SkipIf` uses only the two-condition boolean gate; call-type selection via `If` attributes on four body `<Value>` elements (`Inbound`, `Missed`, `Outbound`, `Notanswered`). Even JSON-RPC envelope CRMs MUST use PostValues with a nested `<Array Key="args">`. Additionally: the API method used MUST create a historical/completed record — NOT a planned/scheduled activity. If the scenario calls an activity-creation endpoint, it will create a future todo, not a call log.
5. Every JSON array literal in a Message string uses `{{` and `}}` instead of `[` and `]` (e.g. `{{^^[Variable]^^}}` not `[^^[Variable]^^]`). (Note: Message should not be used for ReportCall/ReportChat per item 4.)
6. If `SearchContacts_PhoneNumbers` is included: a live test with "abc" was performed and confirmed no API error — if this test was not performed, remove the scenario.
7. No CFD scenario (Id starting with "LookupFromCFD_") contains `<Variables>` or `<Outputs>` — only `<Request>` and `<Rules>`.
8. Every `<Variable>` that maps an array field (emails, phone_numbers) uses `<Filter>` as a **direct child** — not wrapped in `<Filters>`. The `<Filter>` element MUST contain a `<Rule>` child unless the array is guaranteed to have exactly one element in all contacts. Confirmed via live test: an empty `<Filter />` (no Rule child) returns an empty value for any array with more than one element. For category arrays: `<Rule Type="Equals" Ethalon="work">emails.category</Rule>`. For typeless arrays: `<Rule Type="Any" Ethalon="">phone_numbers.phone_number</Rule>` (selects first non-empty element).
9. **ReportChat uses PostValues only (same rule as ReportCall, item 4).** Additionally verify: (a) the CRM API method is correct for chat logging — it is often different from the call logging method (e.g. a chatter/message-post endpoint rather than an activity-creation endpoint); (b) if the method takes positional record-ID args, the EntityId is wrapped in a doubly-nested array `[[EntityId]]`; (c) the body `<Value>` uses `&#x0A;` (element text, not attribute) or `&lt;br/&gt;` (per field type) to separate subject from transcript; (d) no `replaceq()`, no Replace chains.
10. All search scenarios use `[SearchText]` as the search input variable — not `[SearchCriteria]` or any other name.
11. All `EntityType` output values are capitalised: `Person`, `Company` — not lowercase.
12. **CreateContactRecordFromClient chaining decision is based on live test:** if the CRM's create endpoint returns only an ID or a minimal response (confirmed by inspecting the actual create response), the scenario MUST use `<Outputs Next="CreateContactRecordFromClient_Fetch" AllowEmpty="false">` and a companion `_Fetch` scenario. If the create endpoint returns the full record (also confirmed by live test), populate outputs directly — no chain. In either case, do NOT source display fields from 3CX input variables as a substitute for reading the data back from the CRM.
13. **No customer-specific defaults in Parameters:** no `<Parameter>` Default attribute contains a workspace ID, subdomain, database name, org slug, or any other identifier that is unique to the customer whose credentials were used during research — such defaults must be empty (`Default=""`).
14. **No customer-specific references in comments:** XML comments and the file header contain no workspace URLs, subdomain names, database names, user IDs, live-test dates, or any value that identifies the research instance. All field notes are written as general CRM facts, not as observations about the specific instance tested.
15. **`Type="Scenario"` auth structure is correct:** if `Type="Scenario"` is used: (a) `<Authentication>` contains only `<Value>ScenarioId</Value>` — no nested `<Scenario>` element; (b) the auth scenario lives inside `<Scenarios>` with `EntityId=""` and `EntityOrder=""` attributes; (c) it includes `<Rules>`, `<Variables>` (each variable with a `<Filter />` child), and `<Outputs AllowEmpty="false">` with `HeaderName` / `HeaderValue` / `BearerExpiration` — the `<Outputs>` block is mandatory; without it the resolved variable is local to the auth scenario and empty everywhere else.
16. **Phone search uses OR domain:** The base phone lookup scenario (empty Id) and `SearchContacts_PhoneNumbers` both use an OR domain (`|` operator) to match on the sanitized phone field OR the raw phone field. Searching only the sanitized field silently misses contacts whose phone cannot be normalized. **Exception:** if live API testing confirms that the CRM's raw phone field is not filterable (the API returns an `invalid_filter_field` error when filtering on it), the OR domain requirement cannot be met. In that case, filter only on the sanitized/normalized field, document the limitation explicitly in the XML header comment, and omit this pre-check item for that CRM.
17. **Phone output fallback uses `&quot;False&quot;` (capital F):** Any `IIf` that falls back from a sanitized phone field to the raw field checks for `==&quot;&quot;` OR `==&quot;False&quot;` (capital F). Using `==&quot;false&quot;` (lowercase) or `==false` will not match, because 3CX (.NET) converts JSON boolean `false` to the string `"False"`.
18. **Variable paths are absolute and include the response wrapper key.** For JSON-RPC CRMs: all search/read Variable paths are prefixed with `result.` (e.g. `Path="result.id"`, `Path="result.name"`). The only exceptions are scenarios where `result` is itself the target value (auth UID, create record ID): those use `Path="result"` with no suffix. Setting `Path="id"` on a JSON-RPC search response will silently resolve to the envelope's `"id":1` field, not the contact ID.
19. **Domain nesting is three levels deep for execute_kw-style CRMs.** For every search scenario that passes a domain to `execute_kw` (or any method that splats positional args), verify the domain sits at the **third** nesting level inside `<PostValues>`: outer args-array → domain list array → leaf condition arrays. For a single-condition domain this means three `<Array Key="">` elements, not two. Using only two levels produces a flat domain `["field","op","val"]` which Odoo saas-19 (and other strict domain parsers) reject with "invalid item in domain". The correct serialisation is `[[["field","op","val"]]]` at args[5], so that after execute_kw's splatting the method receives domain `[["field","op","val"]]`.
20. **All CRM phone types are mapped, and no phantom types are added:** Every phone type the CRM actually supports has a corresponding `<Variable>` and `<Output>` pair in every contact-returning scenario. At minimum `PhoneBusiness` and `PhoneMobile` must be present if the CRM supports those types; `PhoneBusiness2`, `PhoneHome`, and `FaxBusiness` must also be present if the CRM uses those categories. `PhoneOther` must be present ONLY if the CRM has a native "Other" phone category — do NOT add it as a generic `Type="Any"` catch-all for a CRM that assigns explicit types to all phone entries. No phone type the CRM supports is silently dropped; no type the CRM does not support is fabricated.
21. **Base phone lookup uses partial/suffix matching when CRM stores E.164:** If `Prefix="Plus"` was determined (i.e., the CRM stores full E.164 numbers), the base phone lookup (empty Id) and `LookupFromCFD_Contacts_LookupNumber` MUST use a `$contains`, suffix, or substring operator on the phone field — NOT exact match. Exact match will silently return zero results for any 3CX deployment where MaxLength strips the number to fewer digits than the full international number, because `[Number]` in PostValues carries the stripped value with no Prefix applied. Confirm a suitable partial-match operator was tested live and is used in both scenarios.

Output only the complete, well-formed XML file with no additional explanation.
