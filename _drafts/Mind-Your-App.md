---
title: Mind Your App
date: 2024-06-24 14:00:00 +1000
categories: [mindmap, development]
tags: [mission]
---

## Set the Controls for the Heart of the Sun

Well, it is official now, I've finally embarked on a pet project that I've been meaning to get into for quite some time. I guess this is a bucket list project (there are a few others in that bucket like my "Space Game" for example, but I'll have to get to those later)

Basically what I'm trying to do is write my own Mind Map. And once I get it working to be able to push it onto all the various devices that I own including:

* iPhones
* Android phones and tablets
* MacOS Desktop
* Windows Desktop
* Linux Desktop
* An old Java Pingtel Phone (ok maybe not this one)

Ok, so no small ask then.

## Why would I even consider this?

Why would I even consider embarking on such a journey, you may ask? Well, one of my most loved pieces of software is starting to die:

For many years I've used a fantastic piece of software called [iThoughtsX](https://toketaware.com).

iThoughtsX was one of the first Apple App Store apps and was an amazing success in its day. However, just recently at the start of 2024, its original author (and independent developer) Craig Scott announced that his company toketaWare had ceased trading. :astonished:

Despite the [shock to the community](https://tidbits.com/2024/02/24/toketaware-shuts-down-orphaning-ithoughtsx-mind-mapping-software/) there has been no further communications from Craig, so I guess we are now on our own. 

What does this mean?

* Existing installed versions of the software will continue to run until a future version of macOS, iOS, or Windows causes them to fail.
* If you don't already have a copy of the software, then you can no longer buy it

Just yesterday, I powered up an old iPad and saw that there was an App Store update registered for iThoughtsX but when I tried to initiate the update I was told that the 'App is no longer available in the App Store'. 

Hmmm. Not Happy! :disappointed:

## The dilemma of choice

Others in the [community](https://talk.macpowerusers.com/t/toketaware-is-out-of-business-and-along-with-it-ithoughtsx/36169/4) are asking about their migration options. Some are going to other mind mapping camps such as [SimpleMind](https://simplemind.eu/), [MindNode](https://www.mindnode.com/) or [Xmind](https://xmind.app/), some are jumping camp to go with Canvas based apps like [Freeform](https://apps.apple.com/us/app/freeform/id6443742539) whilst other are crossing over to multi-mode apps like [Curio](https://www.zengobi.com/curio/) and some are going with outliners such as [Obsidian](https://obsidian.md/) (which btw I have really, really tried to like, but it just doesn't work the way I want)

So what happens when a greying developer can't find what he wants?

> WARNING: &nbsp;&nbsp;&nbsp;&nbsp; A New Coding Project is about to Commence!
{: .prompt-warning }

## Requirement Spec

The quest is to create something:
* super simple
* super lightweight
* super low resource consuming
 
Something with just the basic utilitarian features that I need to continue operating with what has become, over the last 10 years, my [Second Brain](https://www.buildingasecondbrain.com/).

Ok here is my initial wish list: (I'm sure there will be "feature creep" on this, but for now this is it!)

1. Runs on any platform (Initial targets being Web + Android [^1])
2. Can run 'offline'
3. Syncs when 'online' - using existing file sharing (let's not build our own, tempting though it is)

## Starting Out

So the first goal is to find a general framework that will allow me to publish the app on as many target platforms as possible, so I can achieve the programmers uptopia of "[Write once, run anywhere](https://en.wikipedia.org/wiki/Write_once,_run_anywhere)"


And looking around, I realise that there's a bunch of really cool web frameworks already out there, such as [React Flow](https://reactflow.dev/), which already gives you a mind map-like interface and already handles all of the sorts of things that I'd like to do with my mind map, however, being such a complete and featureful library has its disadvantages, for example getting it to work with the other libraries I'm going to need to get my app onto mobile devices might be a problem.

Actually most of those things relate to reproducing the feeling and behaviour of the original iThoughts X app.

For example, having a nice panning and scrolling viewport upon which I can have nodes that respond to various auto layout standards 

I guess
Yes, so it's a pity that React Flow is a component-based framework because the sorts of things I want to do are quite customised and I want to take advantage of fairly low-level aspects of the capabilities of JavaScript, CSS and HTML.

And if I start with a nice framework such as React Flow, I'll end up having to reverse engineer it and remake it in many cases to do the sorts of things that I'll be wanting to do.

For example, here's a list of features
that I'd like to pursue as kind of like a minimum viable set of utilitarian features that should be created for this sort of app.
So here they are.
The ability to drag and drop a file from my desktop onto the app or easily upload files into the mind map.

* The ability to access things like Dropbox or Resilio Sync, which is my favorite syncing tool, or perhaps iCloud or even OneDrive.
* Pan around by using the trackpad scrolling (or grab and move viewport when on mobile devices)
* Pinch to zoom in/out
* Local storage + sync (iThoughtsX happily co-operated with cloud storage)

And if you had that file on a shared drive, and you had another machine somewhere else on the internet with that same shared drive and a copy of iThoughts Open,
on that file, then it would just update.
So synchronization between multiple copies of the mind map.

Anyway, there's a lot to do here, so probably I'll need to write a series of articles.
And I guess this first article can be the introductory article.

Anyway, first things first, after looking at React Flow and finding a very nice full featured library, I have reluctantly decided not to use it and to go for my own.
Maybe it's a weakness of mine, but building things from scratch is something that I really enjoy.

So I've reluctantly, I guess, decided to start from scratch.
And starting from scratch means, you guessed it, writing the raw HTML
and JavaScript and style sheets in order to achieve these goals I've set out.

So really my first target is to get to minimum viable functionality, and that would be the ability to display a MindMap, to have the nodes connected with lines that follow the nodes around when you move them, the ability to move the nodes

And obviously that needs to be implemented differently for a web app versus a tablet or phone.

And as I mentioned before, the ability to save the map when you're online and also to hold the contents in local storage for when you're offline.

And later down the track maybe to deal with some of the inevitable synchronisation issues that might arise from doing that.

I guess in order to reach the final destination of being able to write my code and have it available on multiple platforms.

The first thing I've done is really explore how I might be able to have a single code base and satisfy the old paradigm of write once run anywhere.

This naturally led me to looking at Apache Cordova, which I must admit is very impressive.

and I managed to write some simple Cordova apps and publish them as macOS apps which is nice because it uses Electron and Electron is still fairly up to date and well used however unfortunately when I tried to use Cordova to create a Android app I encountered a number of
difficulties.
Which actually now that I think about it, I've learned a bit more since then, I might be able to get around those difficulties.

I might try that actually.
So one of the things that's going to make it easy to write once, run anywhere, would be to adopt
web technology to do this.

Now there's a number of frameworks that allow you to run on a mobile such as Cordova and the way Cordova worked was to use a thing called a webview and what that effectively means is the application that you build and run on your mobile app on your mobile phone is in fact
leveraging the libraries from either the existing or and included web browser library.
This certainly makes it easier if you're going to have a web based version and you want that web based version to also run on mobiles.

However, many of the solutions seem to be a little bit clunky and not so responsive.
I even looked at the latest PWA technology and the ability to, at least with Google, nominate that the PWA is
whatever the term for it is, and have it then available in the Google Play Store.
However, PWA still seem like second class citizens as far as Apple is concerned, so that's kind of ruled that out.

Although I have had some fond experiences with web apps, sorry, not web apps, PWAs, progressive web apps,
So the temptation was to go down that path However It seems that now there's a few new entrants on the scene So as well as react native which Has the advantage of compiling to native code
and using the buttons and widgets that are native to each platform.
It unfortunately needs to be rewritten or modified from pure HTML CSS, i.e.

React flows not really going to work for me.
The next one of interest is Google Flutter.

This also compiles two native code for each platform.

However, the buttons and widgets are drawn rather than using the native platform buttons and widgets.

Also, it's written in Dart, which is yet another language that I'd need to learn.
So for the moment, I've marked that one as a no go.

And as I mentioned Apache Cordova, which uses web views and supports all platform builds out with Electron for us on Mac OS and Windows.

However, in April of 2022, the Microsoft App Center deprecated Cordova support and since then.
There's been a general waning of popularity of the framework.

And in fact, in my experiments, I couldn't even select the target Android version for my now two year old phone.

So that kind of rules that out as well, unfortunately.
Then I looked at other things such as Ionic.
Ionic is quite interesting.
Ionic UI is a component-based UI which is very pretty and works very nicely with a thing called the Capacitor Native Framework.
Ionic's a very mobile UI kit and it works well with Capacitor.
But thankfully, Capacitor can work by itself.

Capacitor is a native framework for mobiles.
It's compatible with plain JavaScript, Angular, React or Vue.
And it happily targets iOS, Android and even web.
And I notice that it claims it now also works with Electron.
I haven't tried that yet though.
So this sounds like this one might be the choice for me.
It is also able to access the huge amount of community Cordova plugins, which kind of gives us lots of features and functions.


----
[^1]: I'm picking Android, since after many years of running a jailbroken iPhone, I finally got sick of the hassle, and switched to a Samsung