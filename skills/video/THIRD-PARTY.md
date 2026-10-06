# Third-party notices

## motion-video-kit (MIT)

`references/critic.md` adapts `critic-prompts.md`, and `references/house-style.md` adapts
`quality-bar.md`, from motion-video-kit (github.com/echris6/motion-video-kit).

```
MIT License

Copyright (c) 2026 echris6

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## lemo-opuscar (MIT)

The treatment discipline in `SKILL.md` and `references/storyboard-template.md` (three candidate
structures, a reason on every focus move, the "differs from the last film" check) and the
four-camera-move minimum in `references/critic.md` are adapted from `DIRECTOR.md` in
lemo-opuscar (github.com/lemomo-ai/lemo-opuscar).

```
MIT License

Copyright (c) 2026 LemoLab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Runtime dependencies (not vendored)

- **GSAP** loads from jsDelivr at render time, under GreenSock's Standard no-charge license. No GSAP code ships in this folder.
- **HyperFrames** is Apache-2.0. The renderer is pinned in `engine/hf/package.json` and installed by npm; it is not vendored here.
- **Kokoro-82M** voice weights are Apache-2.0. They are downloaded at runtime on first use and are not included here.
