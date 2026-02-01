package com.company.apimgmt.repository;

import com.company.apimgmt.entity.TagEntity;
import org.junit.jupiter.api.Test;

import jakarta.inject.Inject;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

public class TagRepositoryTest extends BaseNoDockerRepositoryTest {
    
    @Inject
    TagRepository tagRepository;
    
    @Test
    public void testCreateTag() {
        TagEntity tag = tagRepository.create("test-tag").await().indefinitely();
        
        assertNotNull(tag);
        assertNotNull(tag.id);
        assertEquals("test-tag", tag.name);
        assertNotNull(tag.createdAt);
    }
    
    @Test
    public void testFindByName() {
        tagRepository.create("findable-tag").await().indefinitely();
        
        TagEntity found = tagRepository.findByName("findable-tag").await().indefinitely();
        
        assertNotNull(found);
        assertEquals("findable-tag", found.name);
    }
    
    @Test
    public void testFindByNameNotFound() {
        TagEntity found = tagRepository.findByName("non-existent-tag").await().indefinitely();
        
        assertNull(found);
    }
    
    @Test
    public void testFindAll() {
        tagRepository.create("tag1").await().indefinitely();
        tagRepository.create("tag2").await().indefinitely();
        tagRepository.create("tag3").await().indefinitely();
        
        List<TagEntity> tags = tagRepository.findAll().await().indefinitely();
        
        assertTrue(tags.size() >= 3);
        assertTrue(tags.stream().anyMatch(t -> t.name.equals("tag1")));
        assertTrue(tags.stream().anyMatch(t -> t.name.equals("tag2")));
        assertTrue(tags.stream().anyMatch(t -> t.name.equals("tag3")));
    }
    
    @Test
    public void testDelete() {
        TagEntity tag = tagRepository.create("deletable-tag").await().indefinitely();
        
        Boolean deleted = tagRepository.delete(tag.id).await().indefinitely();
        
        assertTrue(deleted);
        
        TagEntity found = tagRepository.findByName("deletable-tag").await().indefinitely();
        assertNull(found);
    }
    
    @Test
    public void testDeleteNonExistent() {
        Boolean deleted = tagRepository.delete(UUID.randomUUID()).await().indefinitely();
        
        assertFalse(deleted);
    }
    
    @Test
    public void testFindOrCreateWhenNotExists() {
        TagEntity tag = tagRepository.findOrCreate("new-tag").await().indefinitely();
        
        assertNotNull(tag);
        assertNotNull(tag.id);
        assertEquals("new-tag", tag.name);
        assertNotNull(tag.createdAt);
    }
    
    @Test
    public void testFindOrCreateWhenExists() {
        TagEntity created = tagRepository.create("existing-tag").await().indefinitely();
        
        TagEntity found = tagRepository.findOrCreate("existing-tag").await().indefinitely();
        
        assertNotNull(found);
        assertEquals(created.id, found.id);
        assertEquals("existing-tag", found.name);
    }
}
