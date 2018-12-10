## 推荐系统 笔记

1. The_YouTube_video_recommendation_system.pdf
   1. 相关性定义:    video_A 和 video_B的相关性定义为这两个视频被共同观看的频率, 共同观看次数/ F(video_A, video_B), F 函数是一个标准化函数, 用于衡量两个视频的全局流行程度.
   2. 生成推荐候选集: 以种子(用户看过, 收藏过)的视频做种子, 和他相似的视频都放入推荐集中. 为了解决单一化推荐, 可以增加几层关联视频, 然后求交集.
   3. 排名: 按照视频质量, 用户相关度, 多样化
      1. 质量: These signals include view count (the total number of times a video has been watched), the ratings of the video, commenting, favoriting and sharing activity around the video, and upload time.
      2. 用户相关度: 看和用户口味, 偏好的匹配程度
      3. 然后用线性函数生成一个有排名的列表, 因为只推荐4-60个视频, 因为用户同时会关注多个项目, 所以会考虑减少同一类别的视频推荐(同一个上传者, 同一个channel)
   4. 结果: 使用他们的推荐算法, 用户在主页的点击率占到了60%, 远比Top 浏览(次好), 收藏, 评分效果要好.

