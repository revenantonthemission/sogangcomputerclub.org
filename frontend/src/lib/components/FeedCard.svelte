<script lang="ts">
    import type { PostSummary } from '$lib';

    let { data }: PostSummary = $props();
</script>

<a href={data.url} class="flex h-40 items-center w-full" aria-label="Post Card">
    <div class="w-70 h-full m-4 flex-shrink-0 overflow-hidden">
        <img
            src={data.thumbnailUrl}
            class="w-full h-full rounded-lg object-cover aspect-video"
            alt=""
        />
    </div>
    <div class="h-full flex flex-col justify-between">
        <div>
            <h2 class="text-2xl font-bold line-clamp-1 text-white font-[Pretendard_Variable]">{data.title}</h2>
            <p class="text-sm text-white line-clamp-3 font-[Pretendard_Variable]">{data.excerpt}</p>
        </div>
        <div class="text-xs text-white font-[Pretendard_Variable]">
            <span>{data.author}</span>
            <span>·</span>
            <span>{data.publishedAt}</span>
        </div>
    </div>
</a>
