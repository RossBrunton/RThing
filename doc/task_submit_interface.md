## Task Interface ##

### Submitting Tasks ###
When a task is submitted, this is sent via POST to a URL with the task ID in it (defined in tasks.urls, usually
/task/submit/n):

- `code` The code the user typed.
- `mode` One of "answered", "skipped" or "revealed", if ommitted assumed to be "answered"

The server replies with a JSON object:

- `output (string)` The output of the code.
- `isError (boolean)` Whether the output is an error or not.
- `isCorrect (boolean)` Whether the output is correct or not.
- `revealed (boolean)` Whether the answer was a reveal or not. True iff `mode` was "revealed"
- `frags (array)` An array of fragments to display, as described below.
- `image (optional string)` Image data as a data URI if it exists.

### Modes ###
The modes are as follows:

- `answered` Read the code provided, and treat it as an answer (the user typed and submitted some code).
- `skipped` Skip this question and move onto the next task (the user clicked "skip").
- `revealed` If allowable, reveal the answer to the student and continue onto the next task (the user clicked "reveal")

### Fragments ###
Fragments are basically elements to add to the document in specific places. When submitting a task the server returns an
array of fragment objects, each one has the following properties.

- `type (string)` - One of "lesson-start", "lesson-end", "section-start", "section-end", "task", "task-content" or
"prompt-entry".
- `order (string)` - Order value, a string in the form "1" (sections) or "1-1" (tasks).
- `id (optional integer)` - For task, task-content and prompt-entry only; the relevant task.
- `select (optional string)` - For task-content only, the selector to replace.
- `html (string)` - HTML body of fragment.

### Fragment Types ###
The types (where in the document they are inserted) are as follows:

- `lesson-start` - The lesson's introductory text.
- `lesson-end` - The lesson's closing remarks and a link back to the course page.
- `section-start` - The start of a section, including it's title and introduction.
- `section-end` - The end of a section, containing it's closing remarks.
- `task` - A task, including the description, the prompt and empty divs for holding error, skip and after texts.
- `task-content` - Contents of a task, the `id` is the task to change, the `select` is a CSS selector to select an
element inside this task and `html` is the content to set the selected element. It is used to set the error, skip and
after texts.
- `prompt-entry` - A new prompt. Appended to the task's form so that the user can type more code.

### Fragment Ordering ###
Fragments are displayed in the following order in the main element:

- `lesson-start` - Before all other elements except the messages, error and staff options.
- `lesson-end` - After all elements.
- `section-start` - Before any task which has an order with the first half equal to this' order and before lesson-end
- `section-end` - Before any task which has an order with the first half greater to this' order and before lesson-end
- `task` - Before any task which has a greater order, a section-end with the same order, or lesson-end
