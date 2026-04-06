// ---
// title: Catching the Krug
// source: Codeforces 2152B
// difficulty: 1300
// tags: games, math, proof
// keywords: krug, wall, fence
// ---

#set text(region: "GB", font: "New Computer Modern", size: 11pt)

= Catching the Krug

#text(red)[_One observation, all the implications_]

Problem link: #text(blue)[#link("https://codeforces.com/contest/2152/problem/B")]

#line(length: 100%, stroke: 0.6pt)

== TL;DR/Takeaways

In shorter/simpler problems, there is often a fact that is so important (Lemma 0 in this case), that the entire problem is solved when you keep considering its implications.

== Full solution

*Lemma 0* The Krug will never go towards Doran since he's trying to run away.

The above implies the Krug will always try to run towards the wall(s) that are closer or equally close to him than to Doran. 
Trying to make progress towards any other wall means having to move toward Doran which violates Lemma 0. 
Let's define the following term:

*Fence* Walls that are closer or equally close to the Krug than to Doran.

Now, which fence should the Krug run towards?
Since the Krug stops making further progress along an axis if he reaches a normal (perpendicular) fence, his ideal scenario is hugging both fences which happens at a corner.
In this best possible case (or worst from the Doran's perspective), the answer is
$
max ("Doran's distance to vertical fence", "Doran's distance to horizontal fence")
$
because Doran can move diagonally.
The above expression signifies that if the Krug could choose, it suffices to move toward *only* the fence that is farther from Doran.

When can the Krug NOT choose?
When he will get caught before even reaching his desired fence.
This happens in one of the samples where the Krug is on the same column as Doran.
In that case, obviously the Krug can first move along the shared row/column (and across the other axis) all the way to a wall or fence.
Now, the Krug can move along the other axis but it doesn't matter because Doran can simply mimic the Krug and close in on him like he's at a corner.
Therefore, fences that are equidistant to the Krug and Doran are not actually viable.

Modifying the definition of *fences*,

*Fence* Walls that are strictly closer to the Krug than to Doran.

we have the one-liner solution:
$
max cases(
  cases(
    "Doran's distance to vertical fence" & "if vertical fence exists",
    0 & "otherwise"
  ),
  cases(
    "Doran's distance to horizontal fence" & "if horizontal fence exists",
    0 & "otherwise"
  )
)
$

Code: #text(blue)[#link("https://codeforces.com/blog/entry/146988")]

