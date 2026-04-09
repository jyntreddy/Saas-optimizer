output "endpoint" {
  description = "ElastiCache endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}

output "port" {
  description = "ElastiCache port"
  value       = aws_elasticache_cluster.main.cache_nodes[0].port
}
