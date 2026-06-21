---
title: "Agent13: Building an AI Agent Harness for low VRAM"
date: 2026-05-19 1:00:00 +0000
description: "You don't need a massive context window or a super smart model - you just need to work with the model rather than against it. The journey from frustration with Mistral Vibe to rolling my own Agent13."
categories:
  - Software Development
tags:
  - ai
  - llm
  - agent13
  - python
  - tool-design
---

Making an agent that runs effectively within a small model / small context environment requires a different way of thinking about agent harnesses.

## Key Findings

Before diving into the journey, here are the core insights that shaped Agent13:

- **Stop writing longer system prompts.** The LLM's training instincts are your fallback, so design tools around them, not against them.
- **System prompts stay lean and grow conservatively.** The base is just *"You are a tool using AI assistant,"* with extra bits added only as needed based on run-time options.
- **Full-context compaction breaks small models.** Incremental "journal mode" compaction keeps context lean for the whole session.
- **Saved journals become cheap, high-fidelity agent "memory"** (10-20K tokens) - better than any Memory MCP server I tried.
- **154 lines of tool docs cut to ~82.** Every token matters.

## The LLM is the Customer

The conventional approach used for AI coding assistants is: long system prompts, verbose tool descriptions, pages of do's, don'ts and "make sure's", lots of 'Forcing' and 'One-Shotting' the model to do as it's told.

This doesn't work well because there is this thing called ["lost in the middle"](https://arxiv.org/abs/2307.03172). Instructions buried in the context get ignored, and when this happens the model reverts to basic training data instincts.

Rather than thinking about the model as a misbehaving intelligence that needs lots of discipline and carefully worded guardrails, maybe we should be thinking about it as a "customer" or "collaborator" to understand and work with.

This was the core philosophy I built Agent13 around, and here is what my experience was telling me:

- Loading up system prompts with rules, guardrails, do's and don'ts just means we burn our precious context up before we even start.
- The basic instincts of the model don't get lost, they become the fallback. When the model gets confused, it just sticks to what it knows, so why not make this the rule instead of the exception and get it to work the way it 'naturally' works.
- The LLMs already know how to do things. They have been trained to be AI assistants, so let's keep things simple and just leverage how they already work.

Ok, with all of that said, here is my system prompt:

> You are a tool using AI assistant.

Believe it or not, that is good enough.

If I need it to use tools, I add some more. If I want it to have ability to load skills, I add some more.

But even with these 'extra bits' in the system prompt, they are still lean and mean. The next insight is:

> Context is on a "Need to Know Basis"
{: .prompt-tip }

What does this mean? If the LLM doesn't need to know, then I don't tell it.

For example, the tool description on the read_file tool is very very minimal. I don't tell it upfront about all the amazing different modes it supports - it's going to 'expect' it to work in a certain way anyway, and when it uses the tool 'that way', the tool is designed to understand it, so it just works.

Another example: if something goes wrong with a tool call, the tool will do some extra work, and then give a hint back to the agent about where it might find what it is looking for. eg:

```
Text not found in lines 1-50.

Closest fuzzy match (94.2% similarity):
  Lines 12-13:

  --- SEARCH (what you provided)
  +++ FOUND (closest match in file)

  - if filepath not in _snapshots:
  - _snapshots[filepath] = {}
  + if filepath not in _snapshots:
  +     _snapshots[filepath] = {}

Debugging tips:
  1. Check for exact whitespace/indentation match
  2. Verify line endings match (\r\n vs \n)
  3. The file may have been modified since you last read it
```

### Working with the LLM in Practice

So, rather than fighting the model, I decided to work **with** the model. How did I do this?

When it got confused or did something wrong, I said something like this:

> You're obviously having problems getting that tool to work. Tell me how you would naturally expect the tool to work, and I'll go and change it to make it less confusing for you.

After a few rounds of this sort of 'reflection' conversation, I need to expound on two major points:

> **LLMs do not have meta-awareness.** They don't know *why* they do things, they just 'rationalise' and give you a reasonable sounding excuse - which can lead us in the wrong direction if you are not careful.
{: .prompt-tip }

> **LLMs can 'reflect' on how they went.** They are very good at giving suggestions for how things 'should work' and, guess what, those 'suggestions' are a result of how they are trained.
{: .prompt-tip }

Another prompt that worked really well was:

> Let's pause here and reflect on how you found the tools during this session. Did they work as expected? Did you find issues? What happened and how did you get around any issues? What suggestions would you make for changes to the tools so they operate in a more intuitive manner? Please update or create the document in the current directory called edit_issues.md and detail your findings with suggestions for improvements.

After a number of iterations of this process I started to see the number of tool failures drastically diminish!

## Journal Mode: Compaction and Memory

Getting the agent to keep a journal along the way for each feature worked so well, I decided to try to get it to do this style of journalling after each turn and then use the journal as a compacted turn in the message history.

This works way better than trying to compact the entire message list into a single message in a single turn.

Why?

- Doing small chunks means we keep it small for the life of the session, AND we change the message history in a way that stays friendly to the kv-cache at the backend. (ie: avoid the dreaded 'prompt-processing' delays I was seeing with Mistral Vibe)
- The traditional compaction approach is to set a threshold and compact the entire history.
- Trying to get a good summary from an LLM when it is already at the limits of its context length just doesn't work. "Lost in the Middle" kicks in and much of what it did during the session doesn't end up in the summary/compaction.

The solution: **journal mode**.

The prompt I use looks like this:

> Since you have just used tools, tersely reflect on each one, then stop.
> 
> - what was your goal when calling the tools
> - what did you achieve with these calls
> 
> Skip where the goal was not achieved

This works **really** well!

Once the LLM has created the 'reflection', this prompt is removed along with the previous turn and all of its associated tool calls, and it is replaced by the LLM's self reflection.

This means it keeps a record of what it was thinking / trying in the context, without having to keep all of the tool call results in the context.

This is important, since tool call results can be MASSIVE and the agent is probably just trying to learn a small fact or position within the code, so once the 'turn' is over, it doesn't need the verbose results... if it did, it can always redo the required tool call.

The end result is that the context stays as a small journal of what the agent is attempting, what it found and where it is up to.

### From Compaction to Memory

Now that I have this working, I've realised the implications are huge.

Each of these journalled sessions represents a 'memory' of everything that was done. I've tried various Memory MCP servers and they all seem to break down over time as the 'memories' become sparse and irrelevant. Even with advanced latent space search techniques, none of these quite beat having exactly what you want already in the context.

So I built save and load commands into the agent. These allow you to work on a 'feature' say, then save the journalled context.

Later when you want to work on that feature again, it's a simple matter of loading the same context into memory, and suddenly the agent has all of the background 'memories' needed for that specific feature.

- It knows the story of the feature all the way from inception through to working
- It knows what was tried and why
- It knows what didn't work and how it was overcome
- It has all of this with a minimal token spend *(Just the facts Ma'am)*
- Typical saved journals are around 10K to 20K tokens

This means you can resume work on a feature days later. The model already knows the codebase, decisions made, mistakes encountered and has no need to re-explore.

Ok, I'll shut up about it here :laughing:

## The Journey to Agent13

### Starting out with Mistral Vibe

After working for a while with [Aider](https://aider.chat/) I tried [opencode](https://github.com/opencode-ai/opencode) and was horrified by the size of the system prompt my poor local model had to digest. Then I gave [Mistral Vibe](https://github.com/mistralai/mistral-vibe) a try and found that I liked it. It worked well with very small models such as Mistral's [Devstral 2](https://mistral.ai/news/devstral-2-vibe-cli/) model (24B parameter).

Mistral Vibe turned out to be a reasonably solid tool. It was built by Mistral (the French company) and optimised for their own models.

Of course, being a lurker on [reddit's LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) group and a keen advocate of small local privacy-focussed models, I naturally wanted to play around with some of the other very promising looking models that were available (at the time) such as [Qwen 2.5](https://qwenlm.github.io/) and even [Kimi K2](https://github.com/moonshotai/kimi-k2) with a very low quants.

Unfortunately their performance was **Terrible!**. Not because the models were bad, but because they just didn't play nice with Mistral Vibe.

The key and very obvious issue was that the Qwen and Kimi models just didn't like Mistral's diff edit format. They could do it, but only after repeated tries.

At first I tried the common approach which everyone uses, which is to **prompt** the tools better. This kind of worked but when the context got longer, the models fell back to what they were trained on which was basically 'find this string', 'replace it with this string' rather than Mistral's "use this diff format to change the file" (Ok I'm paraphrasing this for readability).

This is where I started to realise:

> If they are ignoring the prompt and doing it their own way, why not accommodate that 'way' and make the tools work the way each model expects
{: .prompt-tip }

### Modifying Vibe

With this realisation, I thought 'let's add some different ways of working to each tool', then for each model I play with, keep adding their own preferred way of working.

So I decided to dive in and make my own local fork of Mistral.

This worked great for a while, until I realised that there were so many things I wanted to change about how it worked, that I was probably better off starting from scratch.

### Time to Build my own

Building new code with Vibe was great, but there were so many things that frustrated the heck out of me.

- The whole automatic 'full context' compression - my agent would be zipping along merrily and then a compaction would occur and it would end up brain-dead not knowing what it was doing any more. - Ugh!
- Every new version introduced features I wasn't really interested in, but I ended up spending a lot of time rebasing to their main branch to stay up-to-date.
- Lots of little UI things I didn't like - too many to mention.

So I made the decision to build my own, and keep it super simple with a focus on model agnostic support for small local models (and large ones too of course).

At this point Agent13 was born.

![Baby Agent13]({{ site.baseurl }}/assets/pimg/Agent13 Pram.png "Agent13 as a baby")

## How It Was Built

### Bootstrapping the Chicken with the Egg

Ok, so how did I start coding?

No I didn't use the old fashioned way (Gawd no!), I bootstrapped with an already working agent: Mistral Vibe.

What does this mean? It means I planned the architecture, then the initial code skeleton using Mistral Vibe, then kept developing it until it was able to continue development on itself.

Ok, there were a few moments where I messed things up badly and had to go back to Mistral Vibe, but after a week of going back and forth, I never needed to go back to Mistral again.

Once I had it running, I deliberately stayed within the new code. Occasionally restarting the agent once the tests were stable.

If I had a problem, I'd roll back to the last known good and use that to fix the problems until it could run its own latest version again.

### Minimalist Architecture

Just a few more words on the philosophy:

- Tools are just functions. Wrapped with decorators for control - nothing fancy.
- I used the same TUI library as Vibe ([Textual](https://textual.textualize.io/)). (I tried others like [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit), but Textual is pretty good.)
- Design principle: every token matters, short docstrings beat long ones.
- 154 lines of tool docs reduced to 82ish.

`[table]` before/after docstring comparison

### The Edit Tool

This was the hardest tool to get right, and the most important one to get right. Every failed edit meant a retry, which burned context and sometimes cascaded into confusion. Getting it wrong was expensive.

The edit tool is where the "LLM is the Customer" philosophy got tested the hardest. Every problem I hit, I solved by changing the tool, not by instructing the model better.

#### The Indentation Mystery

The first sign of trouble was corrupted indentation. Edits would come back with the first line of inserted code flushed left, while the remaining lines kept their correct indentation. The obvious suspect was the tool itself, maybe a stray `.strip()` somewhere in the processing pipeline. I spent hours hunting through the code, checking every whitespace-handling function. Nothing. The tool was innocent. I felt like an idiot.

This is where the LLMs' lack of meta-awareness really showed. When I asked the models about the problem, they confidently insisted they had sent the indentation correctly and that the tool must be stripping it. But the llama-swap logs told a different story: they were not sending the initial indent, despite their post-rationalisation excuses. They genuinely had no awareness that they hadn't emitted those leading spaces.

The real culprit? Honestly, I'm not sure, but I suspect it's the training data. Even though there was plenty of Python in the training data, there was never any data with leading whitespace. Most was likely 'complete' Python, which of course starts at indent zero.

The takeaway: you can't fix this by telling the model to behave differently. You have to design the tool around the limitation.

#### First-Line-Only Auto-Correct

Once I understood the problem, I tried a few things:

- An explicit `indent` parameter, models don't proactively discover it, they only react after failures (token-expensive).
- Auto-infer indent from context, caused *double* indentation because models still put spaces in the content.
- Shift all lines by a delta, worked for Qwen (off by ±1) but broke GLM (which strips the first line to 0 but leaves remaining lines correct).

The key insight: **only the first line is ever wrong.** The remaining lines keep their indentation because they're embedded after `\n` characters, which the LLM handles correctly. And critically, different models get the first line wrong in *different ways*. Qwen is off by ±1, GLM strips it to zero. Which confirms this is LLM behaviour, not a pipeline issue.

The final solution: infer the natural indent from context, correct only the first line, leave the rest alone. Both models succeeded on first attempt.

#### Silent Protection: AST Validation and Edit Previews

The most common edit failure was indentation wreckage that the model couldn't see. The tool would return `{"success": true}` and the model would move on, not knowing the file was now broken.

Two additions solved this:

- **`compile()` validation gate** before writing, rejects invalid Python without modifying the file. (I used `compile()` rather than `ast.parse()` because `ast.parse()` accepts `return` at module level, which would produce broken code.)
- **Edit preview** in the result, shows a few lines of context before and after the edit region, so the model can verify indentation at a glance without a separate `read_file` call.

Here's the bit I'm proud of: I left the docstring unchanged. The model discovers validation on failure ("Python syntax error... File NOT modified") and preview on success. No new concepts to learn, no prompt changes. The tool just works better and fails more clearly. (Context is on a 'need to know' basis.)

#### Docstring Trimming: 154 to 82 Lines

This ties back to the "every token matters" principle. The 7 tools' docstrings totalled 154 lines. I cut them to 82, a 47% reduction.

The guiding principle:

> The AI discovers defaults from results, format variants from trying, and behaviour from usage. Docstrings should label what the tool does and name the parameters, not pre-explain everything that will be obvious after one call.
{: .prompt-tip }

One exception: the `delete` mode kept its behavioural note ("deletes the entire line, not just the matched text") because smaller models consistently assumed it removed only the matched substring, a non-obvious behaviour the model can't discover from the result.

One thing tripped me up though. The `end_line` parameter description said "Used with start_line", accurate for `replace_lines` and `delete`, but it actively *taught* the AI that `end_line` alone was invalid for `append` and `prepend`, where it actually works fine. Parameter descriptions should describe what the parameter *is*, not prescribe how it must be combined.

### The Model Stats

So what models did I use and end up using?

- The workhorse was [Qwen 2.5](https://qwenlm.github.io/) 27B which wrote most of the early code.
- The heavy lifting was done by [Kimi K2](https://github.com/moonshotai/kimi-k2) for tricky problems.
- The Human model (me) - Leaning over the shoulder of the workhorses for most things. This was fairly intense early on.
- Documentation-driven development: every feature was recorded as a journal:
  - What was the feature goal
  - What did we try
  - What worked and didn't work
  - How did we overcome the issues
  - What was the final choice made and why

## Conclusion

Agent13 went from frustration with existing tools, through bootstrapping on Mistral Vibe, to a self-hosted agent that develops itself. The journey taught me something that runs counter to the prevailing wisdom in the AI coding assistant space: the answer isn't longer prompts, more guardrails, and bigger context windows. The answer is to stop treating LLMs as misbehaving intelligences that need discipline, and start treating them as collaborators with their own instincts. Work *with* the grain, not against it.

Context is precious - journal it, save it, reuse it. When you stop wasting tokens on verbose instructions and bloated tool results, even small models on low VRAM become remarkably capable.

The next chapter for Agent13 is already underway: I'm adding a REPL mode targeted at visually impaired users. One user in particular has been giving me feedback and requesting changes to make the agent easier to use with their screen reader. Making AI coding tools more accessible feels like a natural extension of the same philosophy - work with the user-base, not against them.

## References

1. [Agent13 on GitHub](https://github.com/psymonryan/agent13)
2. [Mistral Vibe](https://github.com/mistralai/mistral-vibe)
3. [Devstral 2 and Mistral Vibe CLI announcement](https://mistral.ai/news/devstral-2-vibe-cli/)
4. [Qwen 2.5](https://qwenlm.github.io/)
5. [Kimi K2](https://github.com/moonshotai/kimi-k2)
6. [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
7. [Aider - AI Pair Programming in Your Terminal](https://aider.chat/)
8. [opencode](https://github.com/opencode-ai/opencode)
9. [Textual - Python TUI Framework](https://textual.textualize.io/)
