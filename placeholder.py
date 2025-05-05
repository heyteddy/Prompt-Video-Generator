from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

bg = ColorClip((1280,720), color=(200,200,200), duration=10)
txt = TextClip("Placeholder Video", fontsize=48, color="white", size=(1280,720))\
      .set_duration(10).set_position("center")
clip = CompositeVideoClip([bg, txt])
clip.write_videofile("placeholder.mp4", fps=24, codec="libx264")