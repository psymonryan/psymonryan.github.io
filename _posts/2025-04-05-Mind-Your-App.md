---
title: Mind Your App
date: 2025-04-05 12:00:00 +1000
description: Exploring the creation of a cross-platform desktop application using Electron.js to recreate the functionality of iThoughtsX, a popular mind mapping tool. This post covers the architecture, challenges, and lessons learned from building a multi-platform app.
categories:
  - mindmap
  - development
tags:
  - ithoughtsx
---

## Recreating iThoughtsX for Multi-Platform 

Well, it is official now, I've finally embarked on a pet project that I've been meaning to get into for quite some time. I guess this is a bucket list project (there are a few others in that bucket like my "Space Game" for example, but I'll have to get to those later)

Basically what I'm attempting, is to write my own replacement for iThoughtsX. And once I get it working to be able to push it onto all the various devices that I own including:

* iPhones
* Android phones and tablets
* MacOS Desktops
* Windows Desktops
* Linux Desktops
* An old Java Pingtel Phone (ok maybe not this one)

Ok, so no small ask then.

## Why would I even consider this?

Why would I even consider embarking on such a journey, you may ask? Well, one of my most loved pieces of software is now doomed to die:

For many years I've used a fantastic piece of software called [iThoughtsX](https://toketaware.com).

I've been using this software SOOOOO much, that it has become a part of the way I think and work. I have a large number of maps dating back to 2011, some of these are 'journals' and 'knowledge-bases' containing greater than 70,000 nodes.

**iThoughtsX** was one of the first Apple App Store apps and was an amazing success in its day. However, at the start of 2024, its original author (and independent developer) Craig Scott announced that his company toketaWare had ceased trading. :astonished:

Despite the [shock to the community](https://tidbits.com/2024/02/24/toketaware-shuts-down-orphaning-ithoughtsx-mind-mapping-software/) there has been no further communications from Craig, so I guess we are now on our own. 

What does this mean?

* Existing installed versions of the software will continue to run until a future version of macOS, iOS, or Windows
  causes them to fail.
* The promised Android app will never eventuate
* If you don't already have a copy of the software, then you can no longer buy it

Just yesterday, I powered up an old iPad and saw that there was an App Store update registered for iThoughtsX but when I tried to initiate the update I was told that the 'App is no longer available in the App Store'. 

Hmmm. Not Happy! :disappointed:

## The dilemma of choice

Others in the [community](https://talk.macpowerusers.com/t/toketaware-is-out-of-business-and-along-with-it-ithoughtsx/36169/4) are asking about their migration options. Some are going to other mind mapping camps such as [SimpleMind](https://simplemind.eu/), [MindNode](https://www.mindnode.com/) or [Xmind](https://xmind.app/), some are jumping camp to go with Canvas based apps like [Freeform](https://apps.apple.com/us/app/freeform/id6443742539) whilst other are crossing over to multi-mode apps like [Curio](https://www.zengobi.com/curio/) or [Legend](https://legendapp.com/) and some are going with outliners such as [Workflowy](https://workflowy.com/) or [Obsidian](https://obsidian.md/) (which btw I have really, really tried to like, but it just doesn't work the way I want, (although I am editing this file with it :stuck_out_tongue:)

So what happens when a greying developer can't find what he wants?

> WARNING: &nbsp;&nbsp;&nbsp;&nbsp; A New Coding Project is about to Commence!
{: .prompt-warning }

## Requirement Spec

The quest is to create something:
* super simple
* super lightweight
* super low resource consuming
* runs on new and old devices alike
 
Firstly, I need something with just the basic utilitarian features to continue operating with what has become, over the last >10 years, part of building my [Second Brain](https://www.buildingasecondbrain.com/).

Ok here is my initial wish list: (I'm sure there will be "feature creep" on this, but for now this is it!)

1. Run on any platform (Initial targets being Web + Android [^1])
2. Sync using existing file sharing (let's not build our own, tempting though it is)
3. Read and Save to the original iThoughtsX document format (no import / export required)
4. The same basic keyboard commands
5. Reproduce the feeling and behaviour of the original iThoughtsX app.

## Starting Out

My initial goal was to find a framework that would allow for "[Write once, run anywhere](https://en.wikipedia.org/wiki/Write_once,_run_anywhere)" development

I explored options like  [React Flow](https://reactflow.dev/), which looked promising with its mind map-like interface and loads of built-in functionality. However, I ultimately decided against using a React framework for this project for a few key reasons:

- **Performance:** The React virtual DOM overhead when dealing with huge maps
- **Customisation:** If I want highly customised interactions and layouts I'll be stuck with what the components offer and end up having to rewrite them.
- **DOM Manipulation:** This application will involve heavy DOM manipulation for creating, moving, and manipulating nodes. Direct DOM manipulation with JavaScript offers more control and potential for optimisation.
- **Lightweight Footprint:** I aim for a minimal footprint to ensure compatibility with older devices and operating systems.

Instead, I've opted for just plain old javascript, css and python FastAPI at the backend. I'm going to keep it simple and performant so that it will run fast enough to open all of my existing maps, including the HUGE ones, even on older hardware and operating systems.

So my first proof-of-concept target is to get to minimum viable functionality:

* Display and edit a MindMap as an outline (maybe styled something like [Workflowy](https://workflowy.com/))
* Allow iThoughtsX keyboard commands to select and move nodes around

I'll be sharing my progress and demos, as I release them onto my new domain: [ithoughtsx.com](https://ithoughtsx.com)
(Yes I'm amazed this domain came up for only 5 bucks! - It's a sign!)

Stay tuned...

----
[^1]: I'm picking Android, since after many years of running a jailbroken iPhone, I finally got sick of the hassle, and switched to a Samsung
