# Installed Libraries

Core Intelligence:
- google-cloud-aiplatform (for Gemini Flash API)
- sqlite3 (database)

System Integration:
- psutil (system monitoring)
- pywin32 (Windows-specific operations)
- pyobjc-framework-Cocoa (macOS-specific operations)

User Interface:
- PySide6 (UI framework)
- material-widgets (Material Design)

Network & Communication:
- paho-mqtt (IoT communication)
- httpx (HTTP client)
- elasticsearch (search capabilities)

Billing:
- stripe (payment processing)
- flask (webhook handling)
- pydantic (data validation)

Security:
- cryptography (security operations)
- python-magic (file type validation)

Utilities:
- watchdog (file system monitoring)
- python-dotenv (environment management)
- loguru (logging)



Search in video
Introduction
0:00
[Music]
0:03
[Applause]
0:05
hi welcome to another video so I
About VectorShift
0:08
recently told you guys how you can
0:10
create AI apps quite easily by combining
0:14
Klein and Vector shift and we also
0:16
created a fully working app with it
0:19
where we made the whole AI backend which
0:21
was just amazing to use I asked many of
0:24
you guys in that video if you wanted me
0:26
to create a full video explaining all
0:29
the stuff about Vector shift and if you
0:31
wanted me to create a whole personal
0:33
assistant with it as well and many of
0:36
you said
0:37
yes so today I'll be telling you how you
0:40
can use Vector shift from Basics and how
0:43
you can create an AI personal assistant
0:46
that can read your emails notes and
0:49
everything you want with a simple to use
0:52
no code
0:54
interface you don't need to be a
0:55
programmer to do all this stuff you can
0:58
do it easily via a simpl to use
1:01
interface which is arguably the best
1:03
part about it plus it also has a very
1:07
generous free tier which is great for my
1:09
use cases now many of you may not know
1:13
about Vector shift so let me just give
1:16
you a quick brief it's an AI platform
1:19
that allows you to build pipelines of AI
1:22
workflows for example you can attach an
1:25
llm with notion to make it an AI
1:28
summarizer for your notes or you can
1:30
even attach more things like a knowledge
1:32
base or your Gmail or Google Calendar to
1:36
an llm making it customizable to your
1:40
needs plus it also allows you to create
1:43
chat Bots over those pipelines along
1:46
with automations and other stuff which
1:48
we'll see going forward in the
1:50
video that's the major stuff about it in
1:53
brief but let's get into it and I'll
1:56
show you how it works and how you can
1:58
create a whole personal AI assistant
2:01
along with a
2:02
chatbot so just get yourself signed up
How To Use & Create AI Assistants
2:06
and you'll end up on this page now
2:08
here's the first option which is the
2:10
pipeline option this is one of the major
2:13
options because many other features
2:15
depend on this so let me tell you about
2:18
it pipelines are basically workflows
2:22
that you can create like connecting llms
2:25
to multiple apis and stuff like that you
2:28
can create pipelines e either from
2:30
scratch or from templates templates are
2:33
workflows created by other people and
2:36
Vector shift that you can use as a base
2:39
let's start from scratch here once you
2:42
start from scratch you'll see these
2:44
options first of all you can add an
2:47
input here which will basically allow
2:50
you to take that input and forward it to
2:52
an llm or something so it's now added
2:56
here now let's say we are currently
2:58
making a simple check catbot with CLA so
3:02
you can just go to llms and here you can
3:05
add the llm you want to use let's add
3:08
Cloud here now you can just take the
3:11
input and connect it to the prompt here
3:14
now you can see we also need a system
3:17
prompt here generally the system prompt
3:20
is going to be dynamic so let's just
3:23
select the text option here drag it here
3:27
and enter whatever system prompt you
3:29
want to use use then connect it like
3:32
this once that's done you'll want to add
3:35
an output at the end so just select that
3:39
and connect the output to the llm and
3:42
now you have a very simple chat that
3:44
takes user input sends it through an llm
3:48
and gives you an output but that's
3:51
hypothetical how are you supposed to
3:53
test it well you can do that quite
3:56
easily by just hitting the Run button
3:58
here which will open up this panel where
4:00
you can send in your input and if we
4:02
wait a
4:06
bit you'll see that we have the response
4:09
here so this is super cool you can
4:13
create some great stuff quite easily
4:15
with it but it's not limited to that
4:18
either you can also add a bunch of
4:20
Integrations here as well for example
4:24
you can add the knowledge of your emails
4:26
calendar Discord or any of your
4:29
knowledge bases
4:30
Google Docs sheets or almost anything
4:34
for example if you want the llm to have
4:37
the context of your emails you can just
4:39
take the Gmail option add it here and
4:43
connect it with your
4:44
llm now the llm will have the context of
4:48
your emails and you can just add as much
4:51
stuff as you want to create a whole
4:52
personal AI assistant which is just
4:56
amazing now let's say you configure it
4:59
all and make it work well for you but
5:02
you can't always come here and use this
5:04
interface because it's not that
5:06
interactive it's just for
5:09
testing so once you have it figured out
5:13
just click deploy changes here which
5:16
will save your
5:17
workflow once you save it you'll see
5:20
these options beside it here you can
5:23
basically turn your pipeline into a
5:25
chatbot automation search form or bulk
5:30
job automation basically means it will
5:33
automatically run this pipeline at some
5:35
interval of minutes seconds or days
5:38
depending on how you set up the
5:40
automation apart from that you have the
5:43
chatbot option which will turn this
5:46
pipeline into a chatbot where the user
5:48
can interact quite easily with the
5:50
pipeline through a simple pre-built
5:53
interface next you have the search
5:56
option which uses it in a search
5:58
interface for product search and stuff
6:00
like that next you have the form and
6:03
voice chat
6:04
options the form means it will open up
6:07
like a form and voice chat will convert
6:11
it to a speech to speech feature but you
6:14
need to configure your pipeline to have
6:16
speech input and output as
6:19
well apart from this you also have bulk
6:22
jobs which allows you to run multiple
6:25
pipelines at
6:26
once generally most of us would want to
6:29
convert our pipelines to
6:31
chatbots so let's just select that now
6:36
it will ask you what name you want to
6:38
give it once you do that it will show
6:41
these settings for how you want your
6:42
chatbot to look for example you can
6:46
change colors logos and more once you do
6:50
that you can just hit export and it will
6:53
give you a bunch of options to integrate
6:55
it for example you can add it to your
6:58
website or connect it to slack or you
7:02
can also use it as an API to integrate
7:05
it into your
7:06
applications if you don't want to do
7:09
anything you can just open this URL and
7:12
share it with anyone and they'll be able
7:14
to access the
7:16
chatbot if you ask it to do anything it
7:19
will do it for you based on how you've
7:21
set up the pipeline it's really cool to
7:24
see for sure so that's the major stuff
7:28
about Pipelines and how you can use
7:31
them let me also give you a quick
7:33
overview of the other features as well
7:36
the next one is the marketplace which is
7:39
the same as the pipeline template
7:42
Marketplace next you have the knowledge
7:45
tab here you can create a knowledge base
7:48
for a specific thing by uploading
7:50
documents and you can reference the
7:52
knowledge base in the pipeline for
7:55
context then you have the files option
7:59
which allows you to upload files and
8:01
reference them in the knowledge base or
8:03
pipelines as well you also have
8:07
automations which allow you to trigger
8:09
specific pipelines based on specific
8:11
triggers from different
8:13
applications or you can trigger
8:15
pipelines based on a time interval which
8:18
is cool if you want a fully automated
8:21
workflow next there's the chatbot
8:24
section which will show your chatbots
8:27
and you can edit them and stuff like
8:29
that
8:30
you also have search forms and voice
8:33
Bots which allow you to use your
8:35
pipelines in search form or voice spot
8:39
mode so that's super cool as well next
8:43
you have bulk jobs to process large data
8:46
sets using your pipelines so you can
8:49
give pipelines a ton of data at once and
8:52
let it run you also have portals which
8:56
allow you to create a portal for
8:57
customer service document search or a
9:01
multitude of other use cases there's
9:04
also
9:05
evaluations which allows you to evaluate
9:07
your pipelines by giving you speed
9:10
statistics and stuff like that there's
9:13
also
9:14
transformation which allows you to
9:16
integrate your custom python code into
9:19
pipelines as
9:20
well next you have analytics which gives
9:24
you a bunch of statistics about your
9:26
pipelines as well it's not easy to cover
9:29
all the stuff in just one video because
9:31
there are too many use cases for it so
9:35
let me know if you would like more
9:37
videos on how to use it in different
9:40
ways I think this is great for sure you
9:43
can create whole AI assistants and other
9:46
things with just a drag and drop
9:48
interface which is great overall it's
9:51
pretty cool anyway let me know your
Ending
9:55
thoughts in the comments if you liked
9:57
this video consider donating to my
9:59
Channel Through the super thanks option
10:02
below or you can also consider becoming
10:05
a member by clicking the join
10:08
button also give this video a thumbs up
10:12
and subscribe to my channel I'll see you
10:14
in the next video till then bye
10:22
[Music]


