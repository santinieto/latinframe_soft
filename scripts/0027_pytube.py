from pytube import YouTube

yt = YouTube('http://youtube.com/watch?v=5xtGXlgVMNk')

print('parameters', dir(yt))
print()
print('- yt.title:', yt.title)
print('- yt.author:', yt.author)
print('- yt.captions:', yt.captions)
print('- yt.channel_id:', yt.channel_id)
print('- yt.channel_url:', yt.channel_url)
print('- yt.check_availability:', yt.check_availability)
print('- yt.description:', yt.description)
print('- yt.keywords:', yt.keywords)
print('- yt.length:', yt.length)
print('- yt.publish_date:', yt.publish_date)
print('- yt.rating:', yt.rating)
print('- yt.video_id:', yt.video_id)
print('- yt.views:', yt.views)