---
title: "Agent13: Building an AI Agent Harness for low VRAM"
date: 2026-05-19 1:00:00 +0000
description: "You don't need a massive context window or a super smart model — you just need to work with the model rather than against it. The journey from frustration with Mistral Vibe to rolling my own Agent13."
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

## Introduction

The conventional approach used for AI coding assistants is: long system prompts, verbose tool descriptions, pages of do's, don'ts and "make sure's", lots of 'Forcing' and 'One-Shotting' the model to do as it's told.

This doesnt work well because there is this thing called: "lost in the middle". Instructions buried in the context get ignored, and when this happens the model reverts to basic training data instincts.

Rather than thinking about the model as a misbehaving intelligence that needs lots of discipline and carefully worded guardrails, maybe we should thinking about it as a "customer" or "colaborator" to understand and work with.

This post traces the journey from frustration with Mistral Vibe through to building **Agent13**, and the core insights that shaped the philosophy during the build.

## Background

### Starting out with Mistral Vibe

After working for a while with Aider I tried opencode and was horrified by the size of the system prompt my poor local model had to digest. Then I gave Mistral Vibe a try and found that I liked it. It worked well with very small models such as Mistral's devstral2 model (24B parameter)

Mistral Vibe turned out to be a reasonably solid tool. It was built by Mistral (the French company) and optimised for their own models.

Of course being a lurker on reddit's locallama group and a keen advocate of small local privacy focussed models, I naturally wanted to play around with some of the other very promising looking models that were available (at the time) such as Qwen 2.5 and even Kimi K2 with a very low quants.

Unfortunately their perfomance was **Terrible!**. Not because the models were bad, but because they just didnt play nice with Mistral Vibe.

The key and very obvious issue was that the Qwen and Kimi models just didnt like Mistral's diff edit format. They could do it, but only after repeated tries.

At first I tried the common approach which everyone uses, which is to **prompt** the tools better. This kindof worked but when the context got longer, the models fell back to what they were trained on which was basically 'find this string', 'replace it with this string' rather than Mistral's "use this diff format to change the file" (Ok I'm paraphrasing this for readability)

- `[image]` mistral devstral logo
- `[image]` {coding agent terminal interface}

This is where I started to realise:

> If they are ignoring the prompt and doing it their own way, why not accomodate that 'way' and make the tools work the way each model expects

### Modifying Vibe

With this realisation, I thought 'lets add some different ways of working to each tool', then for each model I play with, keep adding their own preferred way of working.

So I decided to  dive in and make my own local fork of Mistral.

This worked great for a while, until I realised that there were so many things I wanted to change about how it worked, that I was probably better off starting from scratch.

`[image]` {frustrated developer at laptop}

### Time to Build my own

Building new code with Vibe was great, but there were so many things that frustrated the heck out of me.

- The whole automatic 'full context' compression - my agent would be zipping along merrily and then a compaction would occur and it would end up brain-dead not knowing what it was doing any more. - Ugh!

- Every new version introduced features I wasnt really interested, in but I ended up spending a lot of time rebasing to their main branch to stay up-to-date

- Lots of little UI things I didnt like - too many to mention

So I made the decision to build my own, and keep it super simple with a focus on model agnostic support for small local models (and large ones too of course)

At this point Agent13 was born

[Image] Maxwel Smart themed baby photo maybe

`[image]` {small laptop with terminal}

### The LLM is the Customer

With this new build I figured I'd stick to the tool philosophy that was working for me across multiple models and start treating the LLM as the customer from the outset.

This changes the way you think from the ground up: Here is what my experience was telling me:

- Loading up system prompts with rules, guardrails, do's and don'ts just means we burn our precious context up before we even start.
- The basic instincts of the model dont get lost, they become the fallback. When the model gets confused, it just sticks to what it knows, so why not make this the rule instead of the exeption and get it to work the way it 'naturally' works.
- The LLM's already know how to do things. They have been trained to be AI assistants, so lets keep things simple and just leverage how they already work.

Ok, with all of that said, here is my system prompt:

> You are a tool using AI assistant.

Believe it or not, that is good enough.

If I need it to use tools, I add some more, If I want it to have ability to load skills, I add some more.

But even with these 'extra bits' in the system prompt, they are still lean and mean. The next insight is:

> Context is on a "Need to Know Basis"

What does this mean? If the LLM doesnt need to know, then I dont tell it.

For example, the tool description on the read_file tool is very very minimal, I dont tell it upfront about all the amazing different modes it supports, it's going to 'expect' it to work in a certain way anyway, and when it uses the tool 'that way', the tool is designed to understand it, so it just works.

Another example, if something goes wrong with a tool call, the tool will do some extra work, and then give a hint back to the agent about where it might find what it is looking after. eg:

> insert tool response for fuzzy match

  [image]` {customer service / design thinking illustration}

### Working **with** the LLM

So, rather than fighting the model, I decided to work **with** the model. So how did I do this?

When it got confused or did something wrong, I said something like this:

> You're obviously having problems getting that tool to work. Tell me how you would naturally expect the tool to work, and I'll go an change it to make it less confusing for you.

After a few rounds of this sort of 'reflection' conversation, I need to expound on two major points:

1. LLM's do not have meta-awareness. Ie: they dont know **why** they do things, they just 'rationalise' and give you a reasonable sounding excuse. (which can lead us in the wrong direction if you are not careful)

2. LLM's can 'reflect' on how they went, they are very good at giving suggestions for how things 'should work' and, guess what, those 'suggestions' are a result of how they are trained. (of course)

Another prompt that worked really well was:

> Lets pause here and reflect on how you found the tools during this session, did they work as expected? Did you find issues? What happened and how did you get around any issues? What suggestions would you make for changes to the tools so they operate in a more intuitive manner? Please update or create the document in the current directory called edit_issues.md and detail your findings with suggestions for improvements.

After a number of iterations of this process I started to see the number of tool failures drastically diminish!

### Bootstrapping the Chicken with the Egg

Ok, so how did I start coding?

No I didnt use the old fashion way (Gawd no!), I bootstrapped with and already working agent: Mistral Vibe.

What does this mean? It means I planned the architecture, then the initial code skeleton using Mistral Vibe, then kept developing it until it was able to continue development on itself.

Ok, there was a few moments where I messed things up badly and had to go back to Mistral Vibe, but after a week of going back and forth, I never needed to go back to mistral again.

Once I had it running, I deliberately stayed within the new code. Occasionally restarting the agent once the tests were stable.

If I had a problem, I'd roll back to the last known good and use that to fix the problems until it could run its own latest version again.

- `[image]` {ouroboros / snake eating its own tail}

### Minimalist Architecture

Just a few more words on the philosophy:

- Tools are just functions. Wrapped with decorators for control — nothing fancy.

- I used the same TUI library as Vibe (Textual). (I tried others like prompt_toolkit, but textual is pretty good)

- Design principle: every token matters, short docstrings beat long ones

- 154 lines of tool docs reduced to 82ish.

- `[table]` before/after docstring comparison

- `[image]` {minimalist code editor}

### The Edit Tool

Here are some more details about the journey I took along the path of getting a nicely working edit tool (This tool was the hardest to get right and the most important in terms of token consumption when the model got it wrong)

* Insert a nice journey here

### The Model Stats

So what models did I use and end up using?

- The workhorse was Qwen 2.5/2.6 27B which wrote most of the early code 
- The heavy lifting was done by Kimi K2 for tricky problems
- The Human model (me) - Leaning over the shoulder of the workhorses for most things. This was fairly intense early on.
- Documentation-driven development: every feature was recorded as a journal
  - What was the feature goal
  - What did we try
  - What worked and didnt work
  - How did we overcome the issues
  - What was the final choice made and why

### Incremental Compaction vs Full Compaction

Getting the agent to keep a journal along the way for each feature worked so well, I decided to try to get it to do this style of journalling after each turn and then use the journal as a compacted turn in the message history.

This works way better than trying to compact the entire message list into a single message in a single turn.

Why?

- Doing small chunks means we keep it small for the life of the session

- The traditional compaction approach is to set a threshold and compact the entire history.

- Trying to get a good summary from an LLM when it is already at the limits of its context length, just doesnt work. "Lost in the Middle" kicks in and much of what it did during the session doesnt end up in the summary/compaction.

The solution: **journal mode**. 

The prompt I use looks like this:

> Since you have just used tools, tersely reflect on each one, then stop. 
> 
> - what was your goal when calling the tools
> - what did you achieve with these calls
> 
> Skip where the goal was not achieved

This works **really** well!

Once the LLM has created the 'reflection', this prompt is removed along with the previous turn and all of its associated tool calls and it is replaced by the LLMs self reflection. 

This means it keeps a record of what it was thinking / trying in the context, without having to keep all of the tool call results in the context.

This is important, since tool call results can be MASSIVE and the agent is probably just trying to learn a small fact or position within the code,  so once the 'turn' is over, it doesnt need the verbose results... if it did, it can always redo the required tool call.

The end result is that the context stays as a small journal of what the agent is attempting, what it found and where it is up to.

- `[image]` {journal / notebook writing}

### Context Journals vs Agent "Memory"

Now that I have this working, I've realised the implications are huge.

Each of these journalled sessions represents a 'memory' of everything that was done.
I've tried various Memory MCP servers and they all seem to break down over time as the 'memories' become sparse and irrelevant. Even with advanced latent space search techniques, none of these quite beat having exactly what you want already in the context.

So I built save and load commands into the agent. These allow you to work on a 'feature' say, then save the journalled context.

Later when you want to work on that feature again, its a simple matter of loading the same context into memory, and suddenly the agent has all of the background 'memories' needed for that specific feature.

- It knows the story of the feature all the way from inception through to working
- It knows what was tried and why
- It knows what didnt work and how it was overcome
- It has all of this with a minimal token spend *(Just the facts Maam)*
- Typical saved journals are around 10K to 20k tokens.

This means you can resume work on a feature days later. The model already knows the codebase, decisions made, mistakes encountered and has no need to re-explore.

Ok, I'll shut up about it here :laughing:

- `[image]` {file save dialog / session management UI}

## Conclusion

- Agent13 went from frustration → bootstrapping → self-hosted development
- Core insight: stop writing longer prompts. Build tools that work with the model's inherant nature.
- Context is precious - journal it, save it, reuse it
- 

## References

1. [Agent13 on GitHub](https://github.com/psymonryan)
2. [Mistral Vibe](https://github.com/mistralai/vibe)
3. [Qwen 2.5](https://qwenlm.github.io/)
4. [Kimi K2](https://kimi.moonshot.cn/)
