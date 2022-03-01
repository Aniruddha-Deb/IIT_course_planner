# IIT Course Planner

## About

IIT Course Planner is supposed to be an interactive Courses of Study that you can use to frame and arrange your courses and schedule

Blogs:
- [Data Wrangling in Practice: Dataset Creation from Poorly Structured Sources](https://aniruddhadeb.com/articles/2022/iit-course-planner-1.html#iit-course-planner-1)

## Contribute

Right now, there are two major gripes relating to conditional support:

1. **Handling complex conditionals for courses**: The CS1 course structure is a perfect example of this. One can choose either COL333/COL362 in their core, and the other as department elective. We need a way of representing this in the graph, as well as in the XML (what I had in mind was to use an `<or>...</or>` tag, this would work in any setting, and using dotted lines in the graph). The or tag would also be used in the CS1 PL courses (one of MTL103/4/5), because at the moment, the graph shows all three of them as requisite. There are a few other conditionals for CS1 regarding Minor, but we'll get to that later
2. **Conditional expressions**: Prerequisites often have conditionals such as "ABC123 and any one of BCD142/BCD143/BCD144" or in the case of HUL courses, the condition is "Any two courses from HUL2XX category". Handling conditionals like this both in the dataset as well as in the resulting graph (using dotted arrows or other means) needs to be worked on.

The dataset also doesn't cover all facets of the courses of study:

3. **Minor Dataset Addition**: Datasets for minors/department specializations need to be added
4. **Energy Sciences**: ES1 course data needs to be added. Would be easily fixed by shifting to CoS 21-22 but I'm not sure how many things that would break in the PDF scraping section

I've hardly mentioned the problems in the existing dataset: there are still a lot of broken tags in the courses XML dataset that need to be ironed out, and not to mention the bugs that exist in the CoS itself (MT1 courses don't sum up to 63.5 credits because some 700 level courses mentioned in the schedule but not in text are missing, and these courses also don't have a description of their content or prerequisites anywhere in CoS).

**We need contributors**. Open a pull request if you have fixed any of these (or any new bugs/contributions)!
