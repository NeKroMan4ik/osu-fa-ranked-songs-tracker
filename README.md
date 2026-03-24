a thing I ~~vibecoded~~ made in 3 days to track ranked featured songs in osu! using [ossapi](https://github.com/Liam-DeVoe/ossapi) to search beatmaps and bs4 to scrap fa pages 

as of I'm writing this information about many artists is to be filled but I will get to this in the future

**notes**
- supports all modes

- doublecheck if the songs are actually ranked/unranked since I didn't properly test this thing
- currently it doesn't correctly work with maps labeled as "Explicit" and shows them as unranked (need to look more into this when I'm less lazy https://github.com/ppy/osu-web/issues/7053)
- it doesn't work with artists that have compound names on the fa listing like "Sylvir / sakuraburst", "Yuyoyuppe / DJ'TEKINA//SOMETHING" etc. as it searches by the whole artist name and not the split parts
- if a ranked map's metadata is even slightly different from what's on the fa page, it will show the song as unranked
  - same works the other way: if there are 2 versions of the same song with the exact same metadata, but only one of them is featured while the other is not, and the version that isn't featured is ranked, it will show the song as ranked anyway
