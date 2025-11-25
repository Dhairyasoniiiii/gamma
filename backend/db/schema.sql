-- ============================================
-- GAMMA CLONE DATABASE SCHEMA
-- Complete PostgreSQL Schema for 423 Features
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255),
    avatar_url TEXT,
    
    -- OAuth fields
    google_id VARCHAR(255) UNIQUE,
    microsoft_id VARCHAR(255) UNIQUE,
    oauth_provider VARCHAR(50),
    
    -- Subscription info
    plan VARCHAR(20) DEFAULT 'free', -- free, plus, pro, ultra, team, business
    credits_remaining INTEGER DEFAULT 400,
    credits_reset_date TIMESTAMP,
    subscription_id VARCHAR(255),
    subscription_status VARCHAR(50),
    
    -- Usage tracking
    total_presentations_created INTEGER DEFAULT 0,
    total_ai_generations INTEGER DEFAULT 0,
    last_active_at TIMESTAMP,
    
    -- Preferences
    default_theme_id UUID,
    language_preference VARCHAR(10) DEFAULT 'en',
    email_notifications BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_plan ON users(plan);

-- ============================================
-- WORKSPACES (Team feature)
-- ============================================

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Branding
    logo_url TEXT,
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    font_family VARCHAR(100),
    
    -- Settings
    default_theme_id UUID,
    custom_domain VARCHAR(255),
    remove_branding BOOLEAN DEFAULT FALSE,
    
    -- Plan
    plan VARCHAR(20) DEFAULT 'free',
    max_members INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workspace_members (
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- owner, admin, member, viewer
    invited_by UUID REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id)
);

-- ============================================
-- PRESENTATIONS (Core content)
-- ============================================

CREATE TABLE presentations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    
    -- Ownership
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content (JSONB for flexibility)
    content JSONB NOT NULL DEFAULT '{"cards": []}',
    -- Structure: {"cards": [{"id": "card1", "type": "title", "title": "...", "content": {...}}]}
    
    -- Theme & design
    theme_id UUID,
    custom_theme JSONB,
    
    -- Settings
    settings JSONB DEFAULT '{}',
    -- Structure: {"headerFooter": {...}, "customDomain": "", "passwordProtection": {...}}
    
    -- Metadata
    type VARCHAR(20) DEFAULT 'presentation', -- presentation, document, website, social
    is_template BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    
    -- Generation info
    generated_from VARCHAR(20), -- prompt, template, import, blank
    generation_prompt TEXT,
    ai_model_used VARCHAR(50),
    
    -- Analytics
    view_count INTEGER DEFAULT 0,
    unique_viewers INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP,
    
    -- Version control
    current_version INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_presentations_workspace ON presentations(workspace_id);
CREATE INDEX idx_presentations_owner ON presentations(owner_id);
CREATE INDEX idx_presentations_slug ON presentations(slug);
CREATE INDEX idx_presentations_type ON presentations(type);
CREATE INDEX idx_presentations_template ON presentations(is_template) WHERE is_template = TRUE;

-- ============================================
-- THEMES (100+ themes system)
-- ============================================

CREATE TABLE themes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    
    -- Theme data
    colors JSONB NOT NULL,
    -- Structure: {"primary": "#...", "secondary": "#...", "accent": "#...", "background": "#...", "text": "#..."}
    
    fonts JSONB NOT NULL,
    -- Structure: {"heading": "Inter", "body": "Inter", "headingWeight": "700"}
    
    layout JSONB,
    -- Structure: {"cardStyle": "rounded", "spacing": "comfortable", "borderRadius": "12px"}
    
    -- Categorization
    category VARCHAR(50), -- professional, creative, minimal, bold, dark
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Ownership
    created_by UUID REFERENCES users(id),
    workspace_id UUID REFERENCES workspaces(id),
    is_system_theme BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_themes_category ON themes(category);
CREATE INDEX idx_themes_featured ON themes(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_themes_system ON themes(is_system_theme) WHERE is_system_theme = TRUE;

-- ============================================
-- TEMPLATES (2000+ templates)
-- ============================================

CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Content
    content JSONB NOT NULL,
    theme_id UUID REFERENCES themes(id),
    
    -- Categorization
    category VARCHAR(100) NOT NULL,
    -- business, education, technology, marketing, sales, creative, healthcare, finance, etc.
    
    subcategory VARCHAR(100),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Preview
    preview_url TEXT,
    thumbnail_url TEXT,
    
    -- Metadata
    card_count INTEGER,
    estimated_time INTEGER, -- minutes to complete
    difficulty VARCHAR(20), -- beginner, intermediate, advanced
    
    -- Features
    is_featured BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    
    -- Usage
    usage_count INTEGER DEFAULT 0,
    rating_average DECIMAL(3,2),
    rating_count INTEGER DEFAULT 0,
    
    -- Ownership (system or user-created)
    created_by UUID REFERENCES users(id),
    is_system_template BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_featured ON templates(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_templates_premium ON templates(is_premium);
CREATE INDEX idx_templates_tags ON templates USING GIN(tags);

-- ============================================
-- COLLABORATION
-- ============================================

CREATE TABLE collaborators (
    presentation_id UUID REFERENCES presentations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- viewer, commenter, editor, admin
    invited_by UUID REFERENCES users(id),
    invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_viewed_at TIMESTAMP,
    PRIMARY KEY (presentation_id, user_id)
);

CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    presentation_id UUID REFERENCES presentations(id) ON DELETE CASCADE,
    card_id VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    content TEXT NOT NULL,
    
    -- Threading
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    thread_depth INTEGER DEFAULT 0,
    
    -- Status
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_comments_presentation ON comments(presentation_id);
CREATE INDEX idx_comments_card ON comments(card_id);
CREATE INDEX idx_comments_user ON comments(user_id);

CREATE TABLE suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    presentation_id UUID REFERENCES presentations(id) ON DELETE CASCADE,
    card_id VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    type VARCHAR(20), -- edit, insert, delete
    original_content JSONB,
    suggested_content JSONB,
    
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- VERSION HISTORY
-- ============================================

CREATE TABLE versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    presentation_id UUID REFERENCES presentations(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    
    content JSONB NOT NULL,
    theme_id UUID,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    name VARCHAR(255),
    description TEXT,
    
    -- Snapshot
    is_milestone BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_versions_presentation ON versions(presentation_id, version_number DESC);

-- ============================================
-- ANALYTICS (Detailed tracking)
-- ============================================

CREATE TABLE analytics_events (
    id BIGSERIAL PRIMARY KEY,
    presentation_id UUID REFERENCES presentations(id) ON DELETE CASCADE,
    
    -- Event info
    event_type VARCHAR(50) NOT NULL,
    -- view, card_view, click, time_spent, scroll, download, share, comment
    
    -- Visitor info
    visitor_id VARCHAR(100),
    session_id VARCHAR(100),
    user_id UUID REFERENCES users(id),
    
    -- Card-level tracking
    card_id VARCHAR(100),
    card_index INTEGER,
    
    -- Event data
    data JSONB DEFAULT '{}',
    -- Structure depends on event_type
    
    -- Technical info
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(20), -- desktop, mobile, tablet
    browser VARCHAR(50),
    os VARCHAR(50),
    country VARCHAR(3),
    city VARCHAR(100),
    referrer TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_presentation ON analytics_events(presentation_id);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created_at ON analytics_events(created_at);
CREATE INDEX idx_analytics_visitor ON analytics_events(visitor_id);

-- ============================================
-- AI GENERATIONS (Track all AI usage)
-- ============================================

CREATE TABLE ai_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    presentation_id UUID REFERENCES presentations(id) ON DELETE CASCADE,
    
    -- Generation details
    type VARCHAR(50) NOT NULL,
    -- full_generation, rewrite, translate, improve, image, diagram
    
    prompt TEXT,
    input_content TEXT,
    output_content TEXT,
    
    -- AI model used
    model VARCHAR(100),
    model_provider VARCHAR(50), -- openai, anthropic, stability
    
    -- Credits consumed
    credits_used INTEGER,
    
    -- Performance
    generation_time_ms INTEGER,
    tokens_used INTEGER,
    
    -- Quality
    user_rating INTEGER, -- 1-5
    user_feedback TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_generations_user ON ai_generations(user_id);
CREATE INDEX idx_ai_generations_type ON ai_generations(type);
CREATE INDEX idx_ai_generations_created ON ai_generations(created_at);

-- ============================================
-- SUBSCRIPTION & BILLING
-- ============================================

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id),
    
    -- Plan info
    plan VARCHAR(20) NOT NULL,
    billing_cycle VARCHAR(20), -- monthly, annual
    amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(20), -- active, canceled, past_due, unpaid
    
    -- Stripe integration
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    
    -- Credits
    monthly_credits INTEGER,
    credits_reset_day INTEGER,
    
    -- Dates
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

CREATE TABLE payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES subscriptions(id),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    amount DECIMAL(10,2),
    currency VARCHAR(3),
    status VARCHAR(20),
    
    stripe_payment_intent_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TRIGGERS FOR AUTO-UPDATE
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_presentations_updated_at BEFORE UPDATE ON presentations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_themes_updated_at BEFORE UPDATE ON themes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- INITIAL DATA
-- ============================================

-- Create default admin user
INSERT INTO users (email, password_hash, name, plan, credits_remaining)
VALUES ('admin@gamma-clone.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYuQPyWc.kW', 'Admin User', 'ultra', 20000);

COMMENT ON TABLE users IS 'User accounts with authentication and subscription info';
COMMENT ON TABLE presentations IS 'Main content: presentations, documents, websites';
COMMENT ON TABLE templates IS '2000+ pre-built templates across all categories';
COMMENT ON TABLE themes IS '100+ visual themes for customization';
COMMENT ON TABLE analytics_events IS 'Detailed analytics tracking for all presentations';
