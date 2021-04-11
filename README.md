# matrix-py
 Generates a wall of text in a terminal. Similar to the "Matrix Screen" in the movie, "The Matrix"

![Matrix gif](/matrix.gif)

## Requirements
This only requires the [blessed](https://pypi.org/project/blessed/) library.

## Running
Just run `matrix/matrix.py` in a Command Prompt or Powershell and, it will show an output similar to above. The blessed library should allow this to work in Linux. Just haven't tested it out yet.

### Configuration
There is some configuration values on top of `matrix.py`
```python
# configuration / constant values
max_trails = 10
max_trail_length = 50
color_enabled = True

white_rate = 100
fade_rate = 50
```
* `max_trails` is how many trails can be on the terminal.
* `max_trail_length` is how long the trail can be.
* `color_enabled` if this is False, the output will all be white and no color changes will be applied.
* `white_rate` and `fade_rate` is how long those will last. For example, in the beginning of a trail (if color is enabled) it will be white at first. Then turn into green. `white_rate` will determine the speed from white -> green. Same with `fade_rate` only how fast to fade the character out. 
     * Note: any value above 255 is instant (or disabled) and 0 will just keep the trail there. Mainly because of how it works, it will bug out and keep the trail there.

> Quick Note:
> The code isn't really good. I mainly used this to learn how to use the blessed library. Just decided to put it on GitHub.
