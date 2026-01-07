---
title: From Monolith To Modules
date: 2025-04-27 09:00:00 +1000
description: A step-by-step guide to refactoring a JavaScript monolith into modular components using RequireJS. Learn about the benefits of modularization, common patterns, and how to structure your code for better maintainability and reusability.
categories:
  - javascript
  - development
tags:
  - ithoughtsx
---
## From Monolith to Modules: A Step-by-Step Guide to JavaScript Refactoring with RequireJS

![Refactoring](<../assets/pimg/EnModularisation.png>)

**Target Audience**: This article is for beginning JavaScript developers familiar with the basics of
[RequireJS](https://requirejs.org/).
You have probably already read a few other introductory posts elsewhere, but these articles covered starting
a new project from scratch, where-as you are looking to refactor an existing, large, monolithic JavaScript library into a
more manageable module structure. I'm going to assume you understand the core concepts but need practical guidance on how to
apply them to an existing codebase.

Large JavaScript files can quickly become unwieldy, difficult to maintain, and prone to errors. Breaking them down into
smaller, more manageable modules is a crucial step towards a cleaner, more scalable codebase, especially if you are
using AI to help you along the way.

**Background**: I'm currently using [Aider](https://aider.chat) for AI pair programming in my terminal. I'm using several local large
language models that are only 32B parameters (QwQ and Qwen2.5-Coder-32B) and these really seem to struggle with context
issues once your code base reaches around 1000 lines. This seems to be a particular issue when they try to do editing. When the context
is small, the success rate is high, however when the number of tokens gets past about 50% of the context window, the
LLMs start to have problems with comprehension and instruction following, including creating diff formats for editing files. eg. You may see a lot of this:

```
The SEARCH section must exactly match an existing block of lines including all white space, comments, indentation,
docstrings, etc

# The other 1 SEARCH/REPLACE block were applied successfully.
Don't re-send them.
Just reply with fixed versions of the blocks above that failed to match.
```

This is very frustrating, as the only way around it is to use bigger (payed) models, but even then, they can have the
[same issue](https://huggingface.co/papers/2404.06654) but just at a larger context.

Anyway, its worth keeping the context low, since they are generally smarter, no matter which model you are using, so I
guess, now I have a good excuse to break a lifelong bad habit of leaving all my code in one giant file :grin:

But how do we tackle such a refactoring without introducing a mountain of bugs? The key is to proceed incrementally,
with small isolated changes that can be tested before proceeding.

>CONFESSION: &nbsp;&nbsp; "I just tried a massive refactor in one step and of course it didn't end well"
{: .prompt-warning }

While this article focuses on [RequireJS](https://requirejs.org/), the principles also apply to ES Modules with ```import``` and ```export```.

**The "Big Bang" Anti-Pattern**

Many refactoring attempts fall into the trap of trying to do too much at once – a "big bang" rewrite. This is risky.
Changing numerous parts of our code simultaneously makes it incredibly difficult to pinpoint the source of any issues
that arise. So, let's keep it to small, focused changes, followed by immediate validation. Even if you are using an AI
to refactor for you, you still need to supervise the changes, and your chances of missing issues is less if you are
attempting smaller chunks at a time.


### Step 1: Setting Up RequireJS in Your Project

If you haven't already, you'll need to include [RequireJS](https://requirejs.org/) in your `index.html` file.  Leveraging a CDN like Cloudflare
can improve performance by utilising your user's browser caches.

**index.html modifications:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Your Project Title</title>
  <link rel="stylesheet" type="text/css" href="css/map.css">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="description" content="Your Project Description">
  <!-- Include RequireJS from Cloudflare CDN -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.7/require.min.js"></script>
  <link rel="canonical" href="https://yourproject.com/">
</head>
<body>
  <h1>Your Project Title</h1>
  <div id="tree-container" class="flex-container"></div>
  <script data-main="js/main" src="js/lib/require.js"></script>
</body>
</html>
```

**Explanation:**

*   We've added a ```<script>``` tag pointing to the RequireJS library hosted on Cloudflare.  This ensures that the
    browser caches the library, reducing load times for returning visitors. You could also host this yourself, if like
    me, you want to ensure the application can also run offline.
*   The ```data-main="js/main"``` attribute on the second script tells RequireJS to load and execute the
    ```js/main.js``` file after the library itself is loaded. (we will get to that later)
*   Also, we've deliberately added this second script at the end of the body so that any elements referenced by the code will
    have already been seen earlier by the browser as the page loads.

### Step 2: Identify and Isolate Shared Variables

The goal here is to move all the variables we are sharing into one place, with minimal code changes. This means when we
later start to move the functions and something goes wrong, we will know it is not due to missing variables or scoping issues.
We are solving one of the biggest pain points with this process (that I found) up front.

So now we need to identify any global or scoped variables that are shared across functions within your large javascript library. Unless you are
passing everything as parameters, this one is going to cause you grief if you don't get it right now.

Have a look through your code and see if you can identify them, or better still get your AI assistant to do the hard
work with the following prompt:

```
Give me a list of global variables used in this library, also list out any variables that are scoped locally to the
file. For each variable give me a list of function names that reference it.
```

The goal here isn't to *fix* them just yet, but to understand the scope of the change required. Knowing what functions
use what variables can help to work out where to start.

Let's imagine a scenario where you have a large `map.js` such as I do in my
[iThoughtsX Redux]({% post_url 2025-04-05-Mind-Your-App %}) application that I'm currently building.

This file contains all the logic for managing nodes on a mindmap. For this we're using several global variables: `selectedItems`,
`currentItem`, and `extendDirection`. These variables are accessed and modified by multiple functions within `map.js`.

**Creating a `vars.js` Module**

The first refactoring step is to encapsulate these shared variables into a dedicated module, `vars.js`. This module will
*own* these variables and expose them for use by other parts of the application.

1. **Create `vars.js`:**  Create a new file named `vars.js` in your project.

   ```javascript
   // vars.js
   // eslint-disable-next-line
   define(function () {
     var selectedItems = [];
     var currentItem = null;
     var extendDirection = null;
     var keep_folded = false;
     return {
       selectedItems: selectedItems,
       currentItem: currentItem,
       extendDirection: extendDirection,
       keep_folded: keep_folded,
     };
   });
   ```

   Notice that we're using `define()` to create a module.  The function passed to `define()` defines the module's
   exports. We return an object containing the variables we want to make available to other modules.
   
   (The `eslint-disable-next-line` comment just suppresses my Vim ESLint warning about unused variables in the module.)
   
2. **Now update `map.js` to Require `vars.js`:** Modify your `map.js` file to require the newly created `vars.js` module.

   ```javascript
   define([
     "vars" // Add vars as a dependency (this tells requireJS to load it)
   ], function (vars) { // pass this to our map code so we can reference the vars
     // ... rest of map.js code
   });
   ```

   By adding `"vars"` to the dependency array, RequireJS will load `vars.js` before executing the function. The `vars` argument will then contain the object returned by `vars.js`.

3. **Now we can replace the Global Variables with Module Access:** Now, within `map.js`, replace all instances of the global variables (`selectedItems`, `currentItem`, `extendDirection`) with access through the `vars` module.

   For example, instead of:

   ```javascript
   selectedItems.push(item);
   currentItem = targetElement;
   ```

   We can now use:

   ```javascript
   vars.selectedItems.push(item);
   vars.currentItem = targetElement;
   ```


### Step 3: Configuring `main.js`

The `main.js` file is the entry point for your application and configures RequireJS. Its best to keep this file small
and just do simple initialisation code here if you need it.

```javascript
// js/main.js
// eslint-disable-next-line
require.config({
  baseUrl: 'js', // Set the base URL for modules
  paths: {
    'vars': 'vars', // Map the 'vars' module to 'js/vars.js'
    'selection': 'selection',
    'map': 'map'
  },
  shim: { // Optional: For libraries that don't use RequireJS modules
    // Example:
    // 'someLibrary': {
    //   deps: ['jquery'],
    //   exports: 'SomeLibrary'
    // }
  }
});

// eslint-disable-next-line
require(['map'], function(mapModule) {
  // Your application initialisation code here.
  // mapModule is your map.js module.
  console.log('Ready');
});
```

**Explanation:**

*   `baseUrl`:  Sets the root directory for all module paths.  In this case, it's `js`.
*   `paths`:  A mapping of module names to their file paths.  For example, `'vars'` maps to `js/vars.js`.
*   `shim`:  Used for libraries that don't follow the RequireJS module definition.  It tells RequireJS how to load the library and what global variable it exports. (Optional).
*   `require(['map'], function(mapModule) { ... });`: This is the core of the configuration.  It tells RequireJS to load the `map` module and then execute the function when it's loaded. The `mapModule` argument will contain the exports of the `map.js` module.

Ok, at this point if you have got everthing right, you should be able to run your code again. The index.html now pulls
in requireJS from [Cloudflare](https://cdnjs.com/libraries/require.js) or locally, the index then instructs requireJS to
load the main.js which configures, defines and initialises, and finally loads the entry point for the application.


### Step 4: Test, Test, Test!

   This is the most crucial step.  Run all your existing tests to ensure that the changes haven't
   broken any functionality.  If tests fail, carefully review the changes and ensure you've correctly replaced all
   references to the global variables.


### Step 5: Moving Functions to Modules

Once we have all our shared variables encapsulated in `vars.js` and our tests are passing, we're ready to start moving functions to their own modules.

1. **Identify Logical Groups of Functions:** Continue to look for functions that are closely related and perform a specific task. (Get your AI to help)

2. **Create a New Module:** Create a new module file (e.g., `selection.js`) for the identified group of functions.

3. **Copy and Adapt Functions:** Copy the relevant functions from `map.js` into the new module.  Update them to use the variables from `vars.js` instead of the global variables.  For example:

   ```javascript
   // src/js/selection.js
   define([], function() {
     function selectItem(item) {
       vars.selectedItems.push(item);
     }

     function deselectItems() {
       vars.selectedItems = [];
     }

     return {
       selectItem: selectItem,
       deselectItems: deselectItems
     };
   });
   ```

4. **Update `map.js` to Require the New Module:** Add the new module as a dependency to `map.js`.

   ```javascript
   define([
     "vars",
     "selection" // Add selection as a dependency
   ], function (vars, selection) {
     // ... rest of map.js code
   });
   ```

5. **Replace Function Calls in `map.js`:**  Replace the direct calls to the functions in `map.js` with calls to the module's functions.

   For example, instead of:

   ```javascript
   selectItem(item);
   ```

   We can now use:

   ```javascript
   selection.selectItem(item);
   ```

6. **Test Again!**  Run your tests to verify that the function migration hasn't introduced any regressions.

### Repeat and Refine

Continue this process of identifying, copying, and refactoring functions into modules.  With each step, you'll be making
your codebase more organised, maintainable, and testable. You will also be making things easier for your AI to get its
context around.

For me, each time I refactored another group of functions into modules, I again showed the remaining `map.js` &
`main.js` to [Aider](https://aider.chat) and asked for further suggestions.. and of course since the context size was
slowly shrinking as I progressed, the probability of it being able to edit my files got better and better. Now I can happily run in
[architect mode](https://aider.chat/docs/usage/modes.html#architect-mode-and-the-editor-model) again. (Well mostly :grin:)

**Why this works**

This approach has several benefits:

* **Minimal Changes:** We're making small, isolated changes.
* **No Functional Impact:** We haven't altered any function logic.
* **Easy Rollback:** If anything goes wrong, reverting the changes is straightforward.
* **Validation:** We’ve confirmed that the variables are correctly initialised and accessible.

### Conclusion

This strategy allows you to validate each change in isolation, making it easier to identify and fix any issues that
arise. Remember, small changes, frequent testing, and a clear understanding of your code are the keys to success and
your AI coding assistant will love you for it and get [a lot less confused](https://aider.chat/docs/troubleshooting/edit-errors.html)
as you will be able to present a much smaller codebase to it :tongue:
