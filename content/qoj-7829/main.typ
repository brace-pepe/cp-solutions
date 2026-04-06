// ---
// title: Equal Digits
// source: QOJ 7829
// difficulty: 1500
// tags: dp, combinatorics
// keywords: dp optimization, dp trick
// ---

#set text(region: "GB", font: "New Computer Modern", size: 11pt)

= Equal Digits

#text(red)[_Sometimes, just writing the formula makes progress..._]

Problem link: #text(blue)[#link("https://qoj.ac/problem/7829")]

#line(length: 100%, stroke: 0.6pt)

== TL;DR/Takeaways

If it's a DP problem, write the recurrence.
No matter how simple or inefficient it is, just write it and take it from there.
The formula may scream an optimization, or signal futility.

== Full solution

The problem _looks_ like DP.
The constraints seem to suggest so as well.
So let's start from there.

So what should the states be?
Since we are dealing with choosing substrings, it definitely makes sense to keep the current index as a state (like most cases).
Is that it?
What about the digits?
Suppose we want to keep the digit '5' in the final string.
If we skip over a '5' once, we can't do it again.
So it also makes sense to keep the set of digits that we skip over.
We'll use a bitmask for this.

Using these states, we formulate the most obvious recurrence:
$
d p [i] [S] = sum_(j > i, \ a[j] = a[i]) d p [j + 1][S] + cases(
  d p [i + 1][S union {a[i]}] & " if" a[i] in.not S,
  0 & " otherwise"
)
$
where $i$ is the current index, $S$ is the set we were talking about and $a$ is the input string.
Unfortunately, the time complexity of calculating this recurrence naively is $O(n^2|S|)$ because of the summation loop in the transition.

Still, hoping that writing the recurrence wasn't completely fruitless, we can observe that the summation loop is over a pretty nice set of indices.
That is, the set of already calculated indices containing the same digit as the current index... +1.

Therefore, we can use an auxillary array $a u x [d][S]$ to keep the required sum for digit $d$ over all $S$. Hence, we can transition as follows:
$
d p [i] [S] = a u x [a[i]][S] + cases(
  d p [i + 1][S union {a[i]}] & " if" a[i] in.not S,
  0 & " otherwise"
)
$
and update $a u x$:
$
a u x [a[i]] [S] "+=" d p [i + 1][S]
$
Now all transitions are $O(1)$ and we have a fast enough total time complexity of $O(n|S|)$.
Since the memory limit is tight, we the need memory saving trick of only keeping $d p$ states of current and previous index which is enough to AC.

Code: #text(blue)[#link("https://qoj.ac/submission/1805361")]

