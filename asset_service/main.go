package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// Asset represents the data structure for an item in our database
type Asset struct {
	ID      primitive.ObjectID `bson:"_id,omitempty" json:"id,omitempty"`
	Name    string             `bson:"name" json:"name"`
	Type    string             `bson:"type" json:"type"`
	OwnerID int64              `bson:"owner_id" json:"owner_id"`
}

// JWTClaims represents the custom claims in our token from the user_service
type JWTClaims struct {
	UserID int64 `json:"user_id,string"`
	jwt.RegisteredClaims
}

var assetCollection *mongo.Collection

func main() {
	// Read the secret key at startup
	jwtSecretFromEnv := os.Getenv("JWT_SIGNING_KEY")
	jwtSecretKey := []byte(jwtSecretFromEnv)

	// --- Database Connection ---
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("FATAL ERROR: MONGO_URI is not set.")
	}
	client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal(err)
	}
	assetCollection = client.Database("asset_db").Collection("assets")
	fmt.Println("MongoDB connected successfully.")

	router := gin.Default()

	// Group all API routes under the "/api" prefix and apply the authentication middleware
	api := router.Group("", authMiddleware(jwtSecretKey))
	{
		api.POST("/assets", createAsset)
		api.GET("/assets", getAssets)
		api.GET("/assets/:id", getAssetByID)
		api.PUT("/assets/:id", updateAsset)
		api.DELETE("/assets/:id", deleteAsset)
	}

	// Health check endpoint (public)
	router.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "Asset service is running"})
	})

	router.Run(":8000")
}

// authMiddleware validates the JWT
func authMiddleware(secretKey []byte) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Authorization header is required"})
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Invalid token format"})
			return
		}

		claims := &JWTClaims{}
		token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return secretKey, nil
		})

		if err != nil {
			if errors.Is(err, jwt.ErrTokenExpired) {
				c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "Token has expired"})
			} else {
				c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "Invalid token"})
			}
			return
		}

		if !token.Valid {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "Invalid token"})
			return
		}

		c.Set("userID", claims.UserID)
		c.Next()
	}
}

// --- CRUD Handlers with Full Logging ---

// createAsset handles POST /api/assets
func createAsset(c *gin.Context) {
	var newAsset Asset
	if err := c.BindJSON(&newAsset); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	userID, _ := c.Get("userID")
	newAsset.OwnerID = userID.(int64)

	result, err := assetCollection.InsertOne(context.TODO(), newAsset)
	if err != nil {
		log.Printf("ERROR: Failed to create asset in MongoDB. Details: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create asset"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"insertedID": result.InsertedID})
}

// getAssets handles GET /api/assets
func getAssets(c *gin.Context) {
	userID, _ := c.Get("userID")
	cursor, err := assetCollection.Find(context.TODO(), bson.M{"owner_id": userID.(int64)})
	if err != nil {
		log.Printf("ERROR: Failed to find assets in MongoDB. Details: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve assets"})
		return
	}

	var assets []Asset
	if err = cursor.All(context.TODO(), &assets); err != nil {
		log.Printf("ERROR: Failed to decode assets from MongoDB cursor. Details: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to decode assets"})
		return
	}

	c.JSON(http.StatusOK, assets)
}

// getAssetByID handles GET /api/assets/:id
func getAssetByID(c *gin.Context) {
	userID, _ := c.Get("userID")
	id := c.Param("id")
	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid asset ID format"})
		return
	}

	var asset Asset
	err = assetCollection.FindOne(context.TODO(), bson.M{"_id": objectID, "owner_id": userID.(int64)}).Decode(&asset)
	if err != nil {
		log.Printf("ERROR: Failed to find asset by ID in MongoDB. Details: %v", err)
		c.JSON(http.StatusNotFound, gin.H{"error": "Asset not found or you do not have permission to view it"})
		return
	}

	c.JSON(http.StatusOK, asset)
}

// updateAsset handles PUT /api/assets/:id
func updateAsset(c *gin.Context) {
	userID, _ := c.Get("userID")
	id := c.Param("id")
	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid asset ID format"})
		return
	}

	var updates bson.M
	if err := c.BindJSON(&updates); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	result, err := assetCollection.UpdateOne(
		context.TODO(),
		bson.M{"_id": objectID, "owner_id": userID.(int64)},
		bson.M{"$set": updates},
	)
	if err != nil {
		log.Printf("ERROR: Failed to update asset in MongoDB. Details: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update asset"})
		return
	}
	if result.MatchedCount == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Asset not found or you do not have permission to edit it"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"updatedCount": result.ModifiedCount})
}

// deleteAsset handles DELETE /api/assets/:id
func deleteAsset(c *gin.Context) {
	userID, _ := c.Get("userID")
	id := c.Param("id")
	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid asset ID format"})
		return
	}

	result, err := assetCollection.DeleteOne(context.TODO(), bson.M{"_id": objectID, "owner_id": userID.(int64)})
	if err != nil {
		log.Printf("ERROR: Failed to delete asset in MongoDB. Details: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete asset"})
		return
	}
	if result.DeletedCount == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Asset not found or you do not have permission to delete it"})
		return
	}

	c.Status(http.StatusNoContent)
}