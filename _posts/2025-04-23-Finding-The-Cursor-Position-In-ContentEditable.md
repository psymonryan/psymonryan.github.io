---
title: Finding The Cursor Position In ContentEditable
date: 2025-04-21 12:00:00 +1000
categories:
  - html5
  - development
tags:
  - mission
  - printf_debugging
---
## Unraveling the Cursor Position: Navigating Edge Cases

### The Problem

When faced with the task of pinpointing the user's cursor within my [iThoughtsX Redux]({% post_url 2025-04-05-Mind-Your-App %}) application's editable content, I initially vibed a solution from my local AI that looks something like this:

```javascript
const selection = window.getSelection();
const range = selection.getRangeAt(0);
let offset = range.startOffset;
console.log("Updated offset:", offset);
```

At first glance this seemed to do what I wanted: as I move the cursor around with arrow keys, I get the offset position logged to the console, however, it seems to lag behind the actual position until I realised I needed to wrap it in some async code to ensure that it correctly waits for the selection object to be updated:

```javascript
requestAnimationFrame(() => {
(above code)
});
```

Once this was done, the lag went away, however, there were still some weird problems, when trying to get it to behave in a  feature identical way to the old [iThoughtsX](https://ithoughtsx.com) application that I'm trying to replicate.

When the entire text within the editable area was selected, and the user then pressed an arrow key, the behaviour of the offset became misleading. Instead of give me the correct character offset after the selection collapsed, the value seemed to be set to 0 or 1. This made it impossible to distinguish between a genuine cursor position at the start or end and one that arrived there after manipulating a full selection.

![Cursor Position Edge Case](<../assets/pimg/cursor_position_after_selection.png>)

## Take 1: Printf Debugging

Perhaps calculating the offset the way the AI indicated was overkill?

After some research, it turns out that doing it this way is the recommended method when you need to handle complex selections. When a user selects text across multiple nodes or even different parts of the DOM tree, the `Range` object accurately captures this. `range.startOffset` always refers to the starting point of that selection, even if it spans multiple elements.

This is more than I need for simply figuring out the cursor position within a `contenteditable` element.

So I decided for a simpler approach. After observing what the values in the selection were doing with some more console logging, I explored the following:

```javascript
requestAnimationFrame(() => {
  const selection = window.getSelection();
  range = selection.getRangeAt(0);
  let offset = range.startOffset;
  console.log("Updated offset:", offset);
  console.log("focus:", selection.focusOffset);
  console.log("anchor:", selection.anchorOffset);
});
```

This showed that the simpler `focusOffset` and `anchorOffset` gave me the same results as pulling the startOffset out of the range object, and it had the added advantage of being able to determine if the user had selected multiple characters, by checking to see if focusOffset and anchorOffset had different values. (depending on if the user has extended the selection to the left or right, the values of these two variables will swap, but if they are different, we know there is a range selected, and if they are the same, we know that only the cursor position is given - perfect!)

So this is an improvement, but still didn't solve the problem of the weird incorrect value seen if the user selects a range of characters and then presses arrow keys to get to the start or end of that range.

## Take 2: Epiphany

Adding another log line to show the contents of the selection object revealed something interesting:

I noticed that the `range.commonAncestor` seems to be a good hint as to what is going on. Normally it is set to the text of the div, but when I right arrow after selecting all text, the commonAncestor becomes the div itself.

*It turns out that when you select the entire text and then use the arrow keys, the browser is essentially collapsing the selection to a caret (a zero-length selection) at one of the boundaries of the previous selection. Hence, the offset becomes 0 or 1 even though it appears that your cursor is at the end of the text in the `contenteditable` element*

Now I can use this information to correctly determine if the user has selected a range, then used the arrow keys without needing to look at the `range.startOffset`, `selection.focusOffset` or `selection.anchorOffset`

```javascript
// If the user presses left or right when all text is selected
// the offsets are wrong since what we get is a new selection of zero length
// and the way we detect this is by checking that the ancestor of this selection is a div
const selection = window.getSelection();
const focusOffset = selection.focusOffset;
const anchorOffset = selection.anchorOffset;
const currentRange = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

if (
  anchorOffset != focusOffset ||
  currentRange.commonAncestorContainer.nodeType === Node.ELEMENT_NODE
) {
  console.log('text is selected or cursor is at start or end')
} else {
  // If the anchor matches the focus, then we allow splitting the rhs text into the new node
  // Update current item's text to left part
  console.log('We can trust focusOffset to indicate where in the text the cursor is')
  }
```
### Conclusion

Ok, here is what I learned:

1) "Don't trust the AI when it comes to complex edge cases" - Ok I knew this one already :smile:.

2) Always test for these edge cases. The browser is doing some complex things behind the scenes and the answer to the problem may not be obvious.

3) Printf Debugging rules yet again.
