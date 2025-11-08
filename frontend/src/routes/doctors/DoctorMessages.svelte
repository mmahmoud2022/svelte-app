<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getCurrentDoctorProfile,
    getDoctorMessages,
    sendMessage,
    type DoctorMessage
  } from '../../lib/api-doctor';
  
  let messages: DoctorMessage[] = [];
  let loading = true;
  let error: string | null = null;
  let selectedConversation: number | null = null;
  let newMessageText = '';
  let sending = false;

  type Conversation = {
    userId: number;
    userName: string;
    messages: DoctorMessage[];
    lastMessage: DoctorMessage;
    unreadCount: number;
  };

  // Group messages by conversation (sender/receiver pair)
  let conversations: Map<number, Conversation> = new Map();
  let currentDoctorUserId: number | null = null;

  onMount(() => {
    void loadMessages();
    // Poll for new messages every 10 seconds
    const interval = window.setInterval(() => {
      void loadMessages();
    }, 10000);
    return () => clearInterval(interval);
  });

  const loadMessages = async () => {
    loading = messages.length === 0;
    error = null;
    try {
      const doctorId = await ensureDoctorId();
      const response = await getDoctorMessages(1, 100);
      messages = response.items || [];
      
      // Group messages by conversation
      const convMap = new Map<number, Conversation>();

      messages.forEach(msg => {
        const otherUserId = msg.sender_id === doctorId ? msg.receiver_id : msg.sender_id;
        const otherUserName = msg.sender_id === doctorId ? 
          msg.receiver?.full_name || 'Utilisateur' : 
          msg.sender?.full_name || 'Utilisateur';

        const conversation = convMap.get(otherUserId) ?? {
          userId: otherUserId,
          userName: otherUserName,
          messages: [],
          lastMessage: msg,
          unreadCount: 0
        };

        conversation.messages.push(msg);

        if (new Date(msg.created_at).getTime() > new Date(conversation.lastMessage.created_at).getTime()) {
          conversation.lastMessage = msg;
        }

        if (!msg.is_read && msg.receiver_id === doctorId) {
          conversation.unreadCount += 1;
        }

        convMap.set(otherUserId, conversation);
      });
      
      // Sort messages within each conversation
      convMap.forEach(conv => {
        conv.messages.sort((a: DoctorMessage, b: DoctorMessage) => 
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
        conv.lastMessage = conv.messages[conv.messages.length - 1];
      });
      
      conversations = convMap;
      if (convMap.size > 0) {
        const firstConversationId = convMap.keys().next().value as number | undefined;
        if (selectedConversation === null && firstConversationId !== undefined) {
          selectedConversation = firstConversationId;
        } else if (selectedConversation !== null && !convMap.has(selectedConversation)) {
          selectedConversation = firstConversationId ?? null;
        }
      } else {
        selectedConversation = null;
      }
    } catch (err: any) {
      console.error('Error loading messages:', err);
      error = 'Erreur lors du chargement des messages';
    } finally {
      loading = false;
    }
  };

  const ensureDoctorId = async (): Promise<number> => {
    if (currentDoctorUserId !== null) {
      return currentDoctorUserId;
    }

    const profile = await getCurrentDoctorProfile();
    const doctorId = profile.user?.id;

    if (doctorId == null) {
      throw new Error('Identifiant utilisateur du médecin introuvable');
    }

    currentDoctorUserId = doctorId;
    return doctorId;
  };

  const isSentByDoctor = (message: DoctorMessage) => 
    currentDoctorUserId !== null && message.sender_id === currentDoctorUserId;

  const handleSendMessage = async () => {
    if (!newMessageText.trim() || !selectedConversation) return;
    
    sending = true;
    try {
      await sendMessage({
        receiver_id: selectedConversation,
        message: newMessageText
      });
      
      newMessageText = '';
      await loadMessages();
    } catch (err: any) {
      console.error('Error sending message:', err);
      alert('Erreur lors de l\'envoi du message');
    } finally {
      sending = false;
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } else if (diffInHours < 48) {
      return 'Hier ' + date.toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } else {
      return date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short'
      });
    }
  };

  const selectConversation = (userId: number) => {
    selectedConversation = userId;
  };

  $: conversationsArray = Array.from(conversations.values()).sort((a, b) => 
    new Date(b.lastMessage.created_at).getTime() - new Date(a.lastMessage.created_at).getTime()
  );

  $: selectedConversationData = selectedConversation ? conversations.get(selectedConversation) : null;
  $: totalUnread = Array.from(conversations.values()).reduce((sum, conv) => sum + conv.unreadCount, 0);
</script>

<div class="flex h-[600px] bg-white rounded-lg border border-gray-200 overflow-hidden">
  <!-- Conversations List -->
  <div class="w-80 border-r border-gray-200 flex flex-col">
    <div class="p-4 border-b border-gray-200 bg-gradient-to-r from-emerald-50 to-teal-50">
      <h2 class="text-lg font-semibold text-gray-900">Messages</h2>
      {#if totalUnread > 0}
        <p class="text-sm text-emerald-600">{totalUnread} non lu{totalUnread > 1 ? 's' : ''}</p>
      {/if}
    </div>
    
    <div class="flex-1 overflow-y-auto">
      {#if loading}
        <div class="flex items-center justify-center py-12">
          <svg class="animate-spin h-6 w-6 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      {:else if conversationsArray.length === 0}
        <div class="text-center py-12 px-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <p class="text-sm text-gray-600">Aucun message</p>
        </div>
      {:else}
        {#each conversationsArray as conversation}
          <button
            on:click={() => selectConversation(conversation.userId)}
            class="w-full p-4 hover:bg-gray-50 transition-colors border-b border-gray-100 text-left {selectedConversation === conversation.userId ? 'bg-emerald-50' : ''}"
          >
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1">
                  <h4 class="font-semibold text-gray-900 truncate">{conversation.userName}</h4>
                  {#if conversation.unreadCount > 0}
                    <span class="px-2 py-0.5 bg-emerald-600 text-white text-xs rounded-full">
                      {conversation.unreadCount}
                    </span>
                  {/if}
                </div>
                <p class="text-sm text-gray-600 truncate">{conversation.lastMessage.message}</p>
                <p class="text-xs text-gray-500 mt-1">{formatTime(conversation.lastMessage.created_at)}</p>
              </div>
            </div>
          </button>
        {/each}
      {/if}
    </div>
  </div>

  <!-- Chat Area -->
  <div class="flex-1 flex flex-col">
    {#if selectedConversationData}
      <!-- Chat Header -->
      <div class="p-4 border-b border-gray-200 bg-gray-50">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <h3 class="font-semibold text-gray-900">{selectedConversationData.userName}</h3>
            <p class="text-xs text-gray-500">
              {selectedConversationData.messages.length} message{selectedConversationData.messages.length > 1 ? 's' : ''}
            </p>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {#each selectedConversationData.messages as message}
          <div class="flex {isSentByDoctor(message) ? 'justify-end' : 'justify-start'}">
            <div class="max-w-xs lg:max-w-md">
              <div class="rounded-lg p-3 {isSentByDoctor(message) ? 'bg-emerald-600 text-white' : 'bg-white border border-gray-200 text-gray-900'}">
                <p class="text-sm">{message.message}</p>
              </div>
              <p class="text-xs text-gray-500 mt-1 {isSentByDoctor(message) ? 'text-right' : 'text-left'}">
                {formatTime(message.created_at)}
                {#if isSentByDoctor(message) && message.is_read}
                  <span class="ml-1">✓✓</span>
                {/if}
              </p>
            </div>
          </div>
        {/each}
      </div>

      <!-- Message Input -->
      <div class="p-4 border-t border-gray-200 bg-white">
        <form on:submit|preventDefault={handleSendMessage} class="flex gap-2">
          <input
            type="text"
            bind:value={newMessageText}
            placeholder="Écrivez votre message..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            disabled={sending}
          />
          <button
            type="submit"
            class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            disabled={sending || !newMessageText.trim()}
          >
            {#if sending}
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            {/if}
          </button>
        </form>
      </div>
    {:else}
      <div class="flex-1 flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p class="text-gray-600">Sélectionnez une conversation</p>
        </div>
      </div>
    {/if}
  </div>
</div>
