/**
 * Editor Store - Zustand
 * Manages presentation editor state
 */

import { create } from 'zustand';

interface Card {
  id: string;
  type: string;
  content: any;
  position: number;
  style?: any;
}

interface Theme {
  id: string;
  name: string;
  colors: any;
  fonts: any;
}

interface Presentation {
  id: string;
  title: string;
  cards: Card[];
  theme: Theme;
  created_at: string;
  updated_at: string;
}

interface Comment {
  id: string;
  card_id: string;
  user_id: string;
  text: string;
  resolved: boolean;
  created_at: string;
}

interface EditorState {
  presentation: Presentation | null;
  selectedCardId: string | null;
  cards: Card[];
  theme: Theme | null;
  isEditMode: boolean;
  collaborators: any[];
  comments: Comment[];
  history: any[];
  historyIndex: number;
  
  // Actions
  setPresentation: (presentation: Presentation) => void;
  setSelectedCard: (cardId: string | null) => void;
  addCard: (type: string, position: number) => void;
  updateCard: (id: string, changes: Partial<Card>) => void;
  deleteCard: (id: string) => void;
  reorderCards: (fromIndex: number, toIndex: number) => void;
  setTheme: (theme: Theme) => void;
  toggleEditMode: () => void;
  addComment: (comment: Comment) => void;
  updateComment: (id: string, changes: Partial<Comment>) => void;
  undo: () => void;
  redo: () => void;
  saveToHistory: () => void;
}

export const useEditorStore = create<EditorState>((set, get) => ({
  presentation: null,
  selectedCardId: null,
  cards: [],
  theme: null,
  isEditMode: true,
  collaborators: [],
  comments: [],
  history: [],
  historyIndex: -1,
  
  setPresentation: (presentation: Presentation) => {
    set({
      presentation,
      cards: presentation.cards || [],
      theme: presentation.theme,
    });
  },
  
  setSelectedCard: (cardId: string | null) => {
    set({ selectedCardId: cardId });
  },
  
  addCard: (type: string, position: number) => {
    const newCard: Card = {
      id: `card-${Date.now()}`,
      type,
      content: {},
      position,
    };
    
    set((state) => {
      const cards = [...state.cards];
      cards.splice(position, 0, newCard);
      
      // Update positions
      cards.forEach((card, index) => {
        card.position = index;
      });
      
      return { cards };
    });
    
    get().saveToHistory();
  },
  
  updateCard: (id: string, changes: Partial<Card>) => {
    set((state) => ({
      cards: state.cards.map((card) =>
        card.id === id ? { ...card, ...changes } : card
      ),
    }));
    
    get().saveToHistory();
  },
  
  deleteCard: (id: string) => {
    set((state) => {
      const cards = state.cards.filter((card) => card.id !== id);
      
      // Update positions
      cards.forEach((card, index) => {
        card.position = index;
      });
      
      return { cards };
    });
    
    get().saveToHistory();
  },
  
  reorderCards: (fromIndex: number, toIndex: number) => {
    set((state) => {
      const cards = [...state.cards];
      const [movedCard] = cards.splice(fromIndex, 1);
      cards.splice(toIndex, 0, movedCard);
      
      // Update positions
      cards.forEach((card, index) => {
        card.position = index;
      });
      
      return { cards };
    });
    
    get().saveToHistory();
  },
  
  setTheme: (theme: Theme) => {
    set({ theme });
    get().saveToHistory();
  },
  
  toggleEditMode: () => {
    set((state) => ({ isEditMode: !state.isEditMode }));
  },
  
  addComment: (comment: Comment) => {
    set((state) => ({
      comments: [...state.comments, comment],
    }));
  },
  
  updateComment: (id: string, changes: Partial<Comment>) => {
    set((state) => ({
      comments: state.comments.map((comment) =>
        comment.id === id ? { ...comment, ...changes } : comment
      ),
    }));
  },
  
  undo: () => {
    const { history, historyIndex } = get();
    if (historyIndex > 0) {
      const prevState = history[historyIndex - 1];
      set({
        cards: prevState.cards,
        theme: prevState.theme,
        historyIndex: historyIndex - 1,
      });
    }
  },
  
  redo: () => {
    const { history, historyIndex } = get();
    if (historyIndex < history.length - 1) {
      const nextState = history[historyIndex + 1];
      set({
        cards: nextState.cards,
        theme: nextState.theme,
        historyIndex: historyIndex + 1,
      });
    }
  },
  
  saveToHistory: () => {
    const { cards, theme, history, historyIndex } = get();
    
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push({ cards: [...cards], theme });
    
    set({
      history: newHistory,
      historyIndex: newHistory.length - 1,
    });
  },
}));
