<script lang="ts">
    import { MemoCard, MemoPlus } from '$lib/components';
    import type { Memo } from '$lib/types';

    let { data } = $props();
    let selectedSort = $state('updated');

    const sortedMemos: Memo[] = $derived.by(() => {
        const originalMemos = [...data.memos];
        
        switch (selectedSort) {
            case 'newest':
                return originalMemos.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
            
            case 'name':
                return originalMemos.sort((a, b) => a.title.localeCompare(b.title));
            
            case 'updated':
                return originalMemos.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());

            default:
                return originalMemos.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        }
    });
</script>

<svelte:head>
    <title>SGCC - 스터디</title>
</svelte:head>

<main class="bg-[#FFF3DF] min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="mb-8">
            <h1 class="text-4xl font-bold text-[#200F4C] mb-4">스터디 메모</h1>
            <p class="text-lg text-[#200F4C] mb-6">
                공부한 내용을 기록하고 관리하세요. 마크다운을 지원합니다.
            </p>
        </div>

        <div class="p-4">
            <label for="sort-select" class="mr-2 font-bold text-[#200F4C]">정렬 기준:</label>
            <select 
                bind:value={selectedSort} 
                id="sort-select" 
                class="p-2 rounded-md bg-[#200F4C] text-[#FFF3DF] focus:outline-none safari-select min-w-48"
                style="-webkit-appearance: none; -moz-appearance: none; appearance: none; background-image: url('data:image/svg+xml;charset=US-ASCII,<svg xmlns=&quot;http://www.w3.org/2000/svg&quot; viewBox=&quot;0 0 4 5&quot;><path fill=&quot;%23FFF3DF&quot; d=&quot;M2 0L0 2h4zm0 5L0 3h4z&quot;/></svg>'); background-repeat: no-repeat; background-position: right 0.7em top 50%; background-size: 0.65em auto;"
            >
                <option value="updated">업데이트순 (최신)</option>
                <option value="newest">만든순 (오래된 순)</option>
                <option value="name">이름순</option>
            </select>
        </div>

        <div class="columns-1 sm:columns-2 md:columns-3 lg:columns-4 xl:columns-5 2xl:columns-6">
            {#each sortedMemos as memo (memo.id)}
                {#if memo.id % 2 == 0}
                    <MemoCard memo={memo} memoColor="#200F4C"/>
                {:else}
                    <MemoCard memo={memo} memoColor="#22949F"/>
                {/if}
            {/each}
            <MemoPlus />
        </div>
    </div>
</main>